import tkinter as tk
from tkinter import font
import time
import threading
import serial
import math

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════
SERIAL_PORT       = "COM13"
BAUD_RATE         = 115200   
WHEEL_DIAMETER_MM = 70.0

SPEED_LIMITS = {
    "NORMAL"      : 80.0,
    "ENFOUISSEMENT": 15.0
}
ZONE_NAMES_FR = {
    "BLACK"  : "ENFOUISSEMENT",
    "WHITE"  : "BLANC",
    "RED"    : "CONFINEMENT",
    "YELLOW" : "TRANSFERT",
    "GREEN"  : "MAINTENANCE",
    "BLUE"   : "DÉCONTAMINATION",
    "UNKNOWN": "INCONNU"
}

confinement_state = {
    "inside"       : False,
    "last_was_red" : False,
}

robot_data = {
    "line"     : 3,
    "color"    : "UNKNOWN",
    "dist"     : 0.0,
    "deg1"     : 0.0,
    "deg2"     : 0.0,
    "obs"      : False,
    "mode"     : 0,
    "spd"      : 0.0,
    "connected": False,
    "logs"     : []
}

ZONE_COLORS = {
    "BLACK"  : "#212121", "WHITE"  : "#f0f0f0",
    "RED"    : "#F44336", "YELLOW" : "#FFC107",
    "GREEN"  : "#4CAF50", "BLUE"   : "#2196F3",
    "UNKNOWN": "#333333"
}
ZONE_TEXT_COLORS = {
    "BLACK": "white", "WHITE" : "black",
    "RED"  : "white", "YELLOW": "black",
    "GREEN": "white", "BLUE"  : "white",
    "UNKNOWN": "white"
}

ser = None
reconnect_flag = False

def connect_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        robot_data["connected"] = True
        robot_data["logs"].append(f"✅ Connexion BLE établie sur {SERIAL_PORT} à {BAUD_RATE} baud")
    except Exception as e:
        robot_data["logs"].append(f"❌ Erreur connexion BLE: {e}")
        robot_data["connected"] = False

def reconnect_serial():
    global ser, reconnect_flag
    if ser and ser.is_open:
        ser.close()
    connect_serial()
    reconnect_flag = False

def send_cmd(cmd):
    if ser and ser.is_open:
        try:
            ser.write((cmd + "\n").encode())
            return True
        except Exception as e:
            robot_data["logs"].append(f"! Erreur d'envoi: {e}")
            robot_data["connected"] = False
            return False
    return False

def serial_reader():
    """Background thread to read data from BLE Serial3"""
    global reconnect_flag
    while True:
        if ser and ser.is_open:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                if line.startswith("DATA:"):
                    for part in line[5:].split(","):
                        key, _, val = part.partition("=")
                        key = key.strip(); val = val.strip()
                        if   key == "line":  robot_data["line"]  = int(val)
                        elif key == "color": robot_data["color"] = val
                        elif key == "dist":  robot_data["dist"]  = float(val)
                        elif key == "deg1":  robot_data["deg1"]  = float(val)
                        elif key == "deg2":  robot_data["deg2"]  = float(val)
                        elif key == "obs":   robot_data["obs"]   = val == "1"
                        elif key == "mode":  robot_data["mode"]  = int(val)
                        elif key == "spd":   robot_data["spd"]   = float(val)
                elif line.startswith("LOG:"):
                    robot_data["logs"].append(line[4:])
            except serial.SerialException:
                robot_data["connected"] = False
                if not reconnect_flag:
                    reconnect_flag = True
                    robot_data["logs"].append("⚠ Connexion BLE perdue - Tentative de reconnexion...")
            except Exception as e:
                pass
        else:
            if reconnect_flag:
                time.sleep(2)
                reconnect_serial()
            else:
                time.sleep(0.5)

class StockeurApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STOCKEUR — Interface de Contrôle BLE")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        self.current_mode = "PILOT"
        self.pressed_keys = set()
        self._speed_alert_active = False

        self._was_connected = False
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.font_title  = tk.font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_label  = tk.font.Font(family="Segoe UI", size=11)
        self.font_small  = tk.font.Font(family="Segoe UI", size=9)
        self.font_big    = tk.font.Font(family="Segoe UI", size=22, weight="bold")
        self.font_mono   = tk.font.Font(family="Courier New", size=10)
        self.font_status = tk.font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_error  = tk.font.Font(family="Segoe UI", size=14, weight="bold")

        self._build_header()
        self._build_pilot_frame()
        self._build_manu_frame()
        self._show_pilot()
        self._bind_keys()
        self._tick()
        self.root.after(500, self._check_initial_connection)

    def _check_initial_connection(self):
        if not robot_data["connected"]:
            robot_data["logs"].append("ℹ Vérifiez que le dongle BLE est branché et appairé")

    def _on_close(self):
        # Enregistre le journal
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename  = f"stockeur_log_{timestamp}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"=== Journal STOCKEUR (BLE) — {timestamp} ===\n\n")
                log_content = self.log_text.get("1.0", "end")
                f.write(log_content)
            print(f"[LOG] Journal sauvegardé : {filename}")
        except Exception as e:
            print(f"[LOG ERROR] {e}")
        
        # Envoi un commend S avant de fermer le fenetre
        send_cmd("S")
        time.sleep(0.1)
        
        if ser and ser.is_open:
            ser.close()
        
        self.root.destroy()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#16213e", height=55)
        hdr.pack(fill="x")

        tk.Label(hdr, text="⬡  STOCKEUR (BLE)", font=self.font_title,
                 bg="#16213e", fg="#e94560").pack(side="left", padx=20, pady=10)

        self.mode_label = tk.Label(hdr, text="MODE : IHM PILOT",
                                   font=self.font_label, bg="#16213e", fg="#a8dadc")
        self.mode_label.pack(side="left", padx=10)

        self.conn_label = tk.Label(hdr, text="● DÉCONNECTÉ",
                                   font=self.font_small, bg="#16213e", fg="#F44336")
        self.conn_label.pack(side="left", padx=10)

        self.reconnect_btn = tk.Button(
            hdr, text="🔄 Reconnecter",
            font=self.font_small, bg="#0f3460", fg="white",
            relief="flat", padx=8, pady=4, cursor="hand2",
            command=self._manual_reconnect)
        self.reconnect_btn.pack(side="left", padx=5)

        self.switch_btn = tk.Button(
            hdr, text="⇄  Passer en IHM MANU",
            font=self.font_small, bg="#e94560", fg="white",
            relief="flat", padx=12, pady=6, cursor="hand2",
            command=self._toggle_mode)
        self.switch_btn.pack(side="right", padx=20, pady=10)
    
    def _manual_reconnect(self):
        """Manual reconnection button handler"""
        robot_data["logs"].append("🔄 Tentative de reconnexion manuelle...")
        reconnect_serial()

    def _build_pilot_frame(self):
        self.pilot_frame = tk.Frame(self.root, bg="#1a1a2e")

        left = tk.Frame(self.pilot_frame, bg="#1a1a2e")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        zone_card = self._card(left, "Zone Actuelle")
        zone_card.pack(fill="x", pady=(0, 8))
        self.zone_label = tk.Label(zone_card, text="UNKNOWN",
                                   font=self.font_big, bg="#333", fg="white",
                                   pady=14, relief="flat")
        self.zone_label.pack(fill="x", padx=10, pady=(0, 10))

        cmd_card = self._card(left, "Commandes")
        cmd_card.pack(fill="x", pady=(0, 8))
        cmd_row = tk.Frame(cmd_card, bg="#0f3460")
        cmd_row.pack(pady=10, padx=10, fill="x")
        self.btn_go = tk.Button(cmd_row, text="▶  GO", font=self.font_label,
                                bg="#4CAF50", fg="white", relief="flat",
                                padx=20, pady=8, cursor="hand2",
                                command=self._pilot_go)
        self.btn_go.pack(side="left", padx=(0, 10))
        self.btn_stop = tk.Button(cmd_row, text="■  STOP", font=self.font_label,
                                  bg="#F44336", fg="white", relief="flat",
                                  padx=20, pady=8, cursor="hand2",
                                  command=self._pilot_stop)
        self.btn_stop.pack(side="left")

        spd_card = self._card(left, "Vitesse")
        spd_card.pack(fill="x", pady=(0, 8))
        self.pilot_spd_label = tk.Label(spd_card, text="0.0 mm/s",
                                        font=self.font_big, bg="#0f3460", fg="#4CAF50")
        self.pilot_spd_label.pack(pady=8)
        self.pilot_spd_alert = tk.Label(spd_card, text="",
                                        font=self.font_error, bg="#0f3460", fg="#F44336",
                                        width=35, anchor="center")
        self.pilot_spd_alert.pack(pady=(0, 6))

        dist_card = self._card(left, "Distance Parcourue")
        dist_card.pack(fill="x", pady=(0, 8))
        self.dist_label = tk.Label(dist_card, text="0.0 mm",
                                   font=self.font_big, bg="#0f3460", fg="#e94560")
        self.dist_label.pack(pady=8)

        sens_card = self._card(left, "Capteurs Ligne")
        sens_card.pack(fill="x", pady=(0, 8))
        sens_row = tk.Frame(sens_card, bg="#0f3460")
        sens_row.pack(pady=8)
        tk.Label(sens_row, text="Gauche", font=self.font_small,
                 bg="#0f3460", fg="#a8dadc").grid(row=0, column=0, padx=20)
        tk.Label(sens_row, text="Droite", font=self.font_small,
                 bg="#0f3460", fg="#a8dadc").grid(row=0, column=1, padx=20)
        self.pilot_left_led  = self._led(sens_row)
        self.pilot_right_led = self._led(sens_row)
        self.pilot_left_led.grid( row=1, column=0, padx=20, pady=5)
        self.pilot_right_led.grid(row=1, column=1, padx=20, pady=5)

        obs_card = self._card(left, "Obstacle")
        obs_card.pack(fill="x")
        self.obs_label = tk.Label(obs_card, text="AUCUN OBSTACLE",
                                  font=self.font_label, bg="#0f3460", fg="#4CAF50", pady=8)
        self.obs_label.pack(fill="x", padx=10, pady=(0, 8))

        right = tk.Frame(self.pilot_frame, bg="#1a1a2e")
        right.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        log_card = self._card(right, "Journal Robot")
        log_card.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_card, bg="#0a0a1a", fg="#a8dadc",
                                font=self.font_mono, state="disabled",
                                relief="flat", padx=8, pady=8, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_manu_frame(self):
        self.manu_frame = tk.Frame(self.root, bg="#1a1a2e")

        left = tk.Frame(self.manu_frame, bg="#1a1a2e")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        zone_card = self._card(left, "Zone Actuelle")
        zone_card.pack(fill="x", pady=(0, 8))
        self.manu_zone_label = tk.Label(zone_card, text="UNKNOWN",
                                        font=self.font_big, bg="#333", fg="white",
                                        pady=14, relief="flat")
        self.manu_zone_label.pack(fill="x", padx=10, pady=(0, 10))

        move_card = self._card(left, "Déplacement Robot")
        move_card.pack(fill="x", pady=(0, 8))
        key_frame = tk.Frame(move_card, bg="#0f3460")
        key_frame.pack(pady=10)

        self.key_buttons = {}
        for symbol, name, row, col in [("↑","up",1,1),("↓","down",3,1),
                                        ("←","left",2,0),("→","right",2,2),("■","space",2,1)]:
            btn = tk.Label(key_frame, text=symbol, font=self.font_big,
                           bg="#16213e", fg="#a8dadc", width=3, height=1,
                           relief="flat", padx=5, pady=5)
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.key_buttons[name] = btn

        spd_card = self._card(left, "Vitesse")
        spd_card.pack(fill="x", pady=(0, 8))
        self.manu_spd_label = tk.Label(spd_card, text="0.0 mm/s",
                                       font=self.font_big, bg="#0f3460", fg="#4CAF50")
        self.manu_spd_label.pack(pady=8)
        self.manu_spd_alert = tk.Label(spd_card, text="",
                                       font=self.font_error, bg="#0f3460", fg="#F44336",
                                       width=35, anchor="center")
        self.manu_spd_alert.pack(pady=(0, 6))

        sens_card = self._card(left, "Capteurs Ligne")
        sens_card.pack(fill="x", pady=(0, 8))
        sens_row = tk.Frame(sens_card, bg="#0f3460")
        sens_row.pack(pady=8)
        tk.Label(sens_row, text="Gauche", font=self.font_small,
                 bg="#0f3460", fg="#a8dadc").grid(row=0, column=0, padx=20)
        tk.Label(sens_row, text="Droite", font=self.font_small,
                 bg="#0f3460", fg="#a8dadc").grid(row=0, column=1, padx=20)
        self.manu_left_led  = self._led(sens_row)
        self.manu_right_led = self._led(sens_row)
        self.manu_left_led.grid( row=1, column=0, padx=20, pady=5)
        self.manu_right_led.grid(row=1, column=1, padx=20, pady=5)

        dist_card = self._card(left, "Distance Parcourue")
        dist_card.pack(fill="x")
        self.manu_dist_label = tk.Label(dist_card, text="0.0 mm",
                                        font=self.font_big, bg="#0f3460", fg="#e94560")
        self.manu_dist_label.pack(pady=8)

        right = tk.Frame(self.manu_frame, bg="#1a1a2e")
        right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        grab_card = self._card(right, "Contrôle Grappin")
        grab_card.pack(fill="x", pady=(0, 8))
        grab_frame = tk.Frame(grab_card, bg="#0f3460")
        grab_frame.pack(pady=10, fill="x")

        self.grabber_btns = {}
        for key, label in [("c","Fermer"),("o","Ouvrir"),("u","Monter"),("d","Descendre")]:
            row_frame = tk.Frame(grab_frame, bg="#0f3460")
            row_frame.pack(fill="x", padx=10, pady=4)
            key_lbl = tk.Label(row_frame, text=f"[{key.upper()}]",
                               font=self.font_label, bg="#16213e", fg="#a8dadc",
                               width=5, relief="flat", padx=4, pady=4)
            key_lbl.pack(side="left", padx=(0, 8))
            tk.Label(row_frame, text=label, font=self.font_label,
                     bg="#0f3460", fg="white", width=10).pack(side="left")
            ind = tk.Label(row_frame, text="●", font=self.font_label,
                           bg="#0f3460", fg="#333")
            ind.pack(side="right", padx=10)
            self.key_buttons[key] = key_lbl
            self.grabber_btns[key] = ind

        log_card_manu = self._card(right, "Journal Robot")
        log_card_manu.pack(fill="both", expand=True)
        self.manu_log_text = tk.Text(log_card_manu, bg="#0a0a1a", fg="#a8dadc",
                                     font=self.font_mono, state="disabled",
                                     relief="flat", padx=8, pady=8, wrap="word")
        self.manu_log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _card(self, parent, title):
        frame = tk.Frame(parent, bg="#0f3460", relief="flat", bd=0)
        tk.Label(frame, text=title.upper(), font=self.font_small,
                 bg="#0f3460", fg="#e94560", anchor="w",
                 padx=10, pady=4).pack(fill="x")
        tk.Frame(frame, bg="#e94560", height=1).pack(fill="x", padx=10)
        return frame

    def _led(self, parent):
        return tk.Label(parent, text="●", font=tk.font.Font(size=22),
                        bg="#0f3460", fg="#333")

    def _log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}]  {msg}\n"
        for widget in [self.log_text, self.manu_log_text]:
            widget.config(state="normal")
            widget.insert("end", entry)
            widget.see("end")
            widget.config(state="disabled")

    def _pilot_go(self):
        if send_cmd("G"):
            self.btn_go.config(bg="#2e7d32")
            self.btn_stop.config(bg="#F44336")
            robot_data["logs"].append("→ Commande GO envoyée")
        else:
            robot_data["logs"].append("❌ Échec d'envoi GO")

    def _pilot_stop(self):
        if send_cmd("S"):
            self.btn_stop.config(bg="#b71c1c")
            self.btn_go.config(bg="#4CAF50")
            robot_data["logs"].append("→ Commande STOP envoyée")
        else:
            robot_data["logs"].append("❌ Échec d'envoi STOP")

    def _toggle_mode(self):
        if self.current_mode == "PILOT":
            self._show_manu()
            send_cmd("N")
            robot_data["logs"].append("→ Passage en IHM MANU")
        else:
            self._show_pilot()
            send_cmd("P")
            robot_data["logs"].append("→ Passage en IHM PILOT")

    def _show_pilot(self):
        self.current_mode = "PILOT"
        self.manu_frame.pack_forget()
        self.pilot_frame.pack(fill="both", expand=True)
        self.mode_label.config(text="MODE : IHM PILOT")
        self.switch_btn.config(text="⇄  Passer en IHM MANU")

    def _show_manu(self):
        self.current_mode = "MANU"
        self.pilot_frame.pack_forget()
        self.manu_frame.pack(fill="both", expand=True)
        self.mode_label.config(text="MODE : IHM MANU")
        self.switch_btn.config(text="⇄  Passer en IHM PILOT")

    def _bind_keys(self):
        self.root.bind("<KeyPress>",   self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

    def _on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.pressed_keys:
            return
        self.pressed_keys.add(key)
        self._highlight_key(key, True)
        if self.current_mode == "MANU":
            if   key == "up":    send_cmd("F"); robot_data["logs"].append("→ AVANT")
            elif key == "down":  send_cmd("B"); robot_data["logs"].append("→ ARRIÈRE")
            elif key == "left":  send_cmd("L"); robot_data["logs"].append("→ GAUCHE")
            elif key == "right": send_cmd("R"); robot_data["logs"].append("→ DROITE")
            elif key == "space": send_cmd("S"); robot_data["logs"].append("→ STOP roues")
            elif key == "u":     send_cmd("U"); robot_data["logs"].append("→ BRAS monter")
            elif key == "d":     send_cmd("D"); robot_data["logs"].append("→ BRAS descendre")
            elif key == "o":     send_cmd("O"); robot_data["logs"].append("→ PINCE ouvrir")
            elif key == "c":     send_cmd("C"); robot_data["logs"].append("→ PINCE fermer")

    def _on_key_release(self, event):
        key = event.keysym.lower()
        self.pressed_keys.discard(key)
        self._highlight_key(key, False)
        if self.current_mode == "MANU":
            if   key in ("up","down","left","right"):
                send_cmd("S"); robot_data["logs"].append("→ STOP roues")
            elif key in ("u","d"):
                send_cmd("X"); robot_data["logs"].append("→ BRAS stop")
            elif key in ("o","c"):
                send_cmd("V"); robot_data["logs"].append("→ PINCE stop")

    def _highlight_key(self, key, pressed):
        mapping = {"up":"up","down":"down","left":"left","right":"right","space":"space"}
        if key in mapping and mapping[key] in self.key_buttons:
            self.key_buttons[mapping[key]].config(
                bg="#e94560" if pressed else "#16213e",
                fg="white"   if pressed else "#a8dadc")
        if key in self.key_buttons and key in ["c","o","u","d"]:
            self.key_buttons[key].config(
                bg="#e94560" if pressed else "#16213e",
                fg="white"   if pressed else "#a8dadc")
            ind = self.grabber_btns.get(key)
            if ind:
                ind.config(fg="#e94560" if pressed else "#333")

    def _tick(self):
        self._update_ui()
        self.root.after(100, self._tick)

    def _update_ui(self):
        
        # connection
        connected = robot_data["connected"]
        self.conn_label.config(
            text="● CONNECTÉ (BLE)" if connected else "● DÉCONNECTÉ",
            fg  ="#4CAF50"          if connected else "#F44336")

        
        if self._was_connected and not connected:
            send_cmd("S")
            robot_data["logs"].append("⚠ Connexion perdue — arrêt automatique")
        self._was_connected = connected

        # distance
        avg_deg = (robot_data["deg1"] + robot_data["deg2"]) / 2.0
        dist_mm = (avg_deg / 360.0) * math.pi * WHEEL_DIAMETER_MM
        self.dist_label.config(     text=f"{dist_mm:.1f} mm")
        self.manu_dist_label.config(text=f"{dist_mm:.1f} mm")


        color = robot_data["color"]

        if self.current_mode == "PILOT" and color in ("RED", "GREEN", "YELLOW"):
            if not getattr(self, "_auto_switched", False):
                self._auto_switched = True
                self._show_manu()
                send_cmd("N")
                robot_data["logs"].append(
                    f"⚡ Auto-switch → IHM MANU (zone {ZONE_NAMES_FR.get(color, color)} détectée)")
        else:
            
            if color not in ("RED", "GREEN", "YELLOW"):
                self._auto_switched = False

        if color == "RED":
            if not confinement_state["last_was_red"]:
                confinement_state["inside"] = not confinement_state["inside"]
                if confinement_state["inside"]:
                    robot_data["logs"].append("→ Entrée en zone de confinement")
                    send_cmd("W") 
                else:
                    robot_data["logs"].append("→ Sortie de zone de confinement")
                    send_cmd("K")  
            confinement_state["last_was_red"] = True
        else:
            confinement_state["last_was_red"] = False

        
        if confinement_state["inside"] and color != "RED":
            display_zone = "ENFOUISSEMENT"
            bg_color     = "#212121"
            txt_color    = "white"
        else:
            display_zone = ZONE_NAMES_FR.get(color, color)
            bg_color     = ZONE_COLORS.get(color, "#333")
            txt_color    = ZONE_TEXT_COLORS.get(color, "white")

        self.zone_label.config(     text=display_zone, bg=bg_color, fg=txt_color)
        self.manu_zone_label.config(text=display_zone, bg=bg_color, fg=txt_color)

        
        line = robot_data["line"]
        l_on = (line == 0 or line == 1)
        r_on = (line == 0 or line == 2)
        self.pilot_left_led.config( fg="#4CAF50" if l_on else "#333")
        self.pilot_right_led.config(fg="#4CAF50" if r_on else "#333")
        self.manu_left_led.config(  fg="#4CAF50" if l_on else "#333")
        self.manu_right_led.config( fg="#4CAF50" if r_on else "#333")

        
        if robot_data["obs"]:
            self.obs_label.config(text="!  OBSTACLE DÉTECTÉ", fg="#F44336")
        else:
            self.obs_label.config(text="AUCUN OBSTACLE",       fg="#4CAF50")

        
        spd        = robot_data["spd"]
        spd_abs    = abs(spd)
        limit      = SPEED_LIMITS["ENFOUISSEMENT"] if confinement_state["inside"] else SPEED_LIMITS["NORMAL"]
        over       = spd_abs > limit

        spd_color  = "#F44336" if over else "#4CAF50"
        alert_text = f"! VITESSE LIMITE DÉPASSÉE ({limit:.0f} mm/s)" if over else ""

        self.pilot_spd_label.config(text=f"{spd_abs:.1f} mm/s", fg=spd_color)
        self.manu_spd_label.config( text=f"{spd_abs:.1f} mm/s", fg=spd_color)
        self.pilot_spd_alert.config(text=alert_text)
        self.manu_spd_alert.config( text=alert_text)

        if over and not self._speed_alert_active:
            self._speed_alert_active = True
            robot_data["logs"].append(
                f"! ALERTE VITESSE — {spd_abs:.1f} mm/s dépasse la limite de {limit:.0f} mm/s")
        elif not over:
            self._speed_alert_active = False

        
        while robot_data["logs"]:
            self._log(robot_data["logs"].pop(0))

if __name__ == "__main__":
    print("=" * 60)
    print("STOCKEUR - Interface de Contrôle BLE")
    print("=" * 60)
    print(f"Port: {SERIAL_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    print("-" * 60)
    
    connect_serial()
    t = threading.Thread(target=serial_reader, daemon=True)
    t.start()
    root = tk.Tk()
    app  = StockeurApp(root)
    root.mainloop()