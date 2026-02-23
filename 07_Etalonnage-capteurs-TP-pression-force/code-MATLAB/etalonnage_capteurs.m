%% ÉTALONNAGE DE CAPTEURS - LECTURE DEPUIS FICHIERS CSV
clear all; close all; clc;

%% 1. CHARGEMENT DES DONNÉES
fprintf('============================================================\n');
fprintf('CHARGEMENT DES DONNÉES\n');
fprintf('============================================================\n');

% Déterminer le chemin du script
script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);
data_dir = fullfile(project_root, 'data');

% Lecture capteur pression
pression_file = fullfile(data_dir, 'capteur_pression.csv');
data_pression = readtable(pression_file);
pression_mmHg = data_pression.pression_mmHg;
tension_mV = data_pression.tension_mV;
tension_V = tension_mV / 1000;

fprintf('✅ Données de pression chargées: %d points\n', length(pression_mmHg));

% Lecture capteur force
force_file = fullfile(data_dir, 'capteur_force.csv');
data_force = readtable(force_file);

% Séparation par gain
idx_gain10000 = data_force.gain == 10000;
idx_gain1000 = data_force.gain == 1000;

poids1 = data_force.poids_g(idx_gain10000);
tension1 = data_force.tension_V(idx_gain10000);

poids2 = data_force.poids_g(idx_gain1000);
tension2 = data_force.tension_V(idx_gain1000);

fprintf('✅ Données de force chargées:\n');
fprintf('   Gain 10000: %d points\n', length(poids1));
fprintf('   Gain 1000: %d points\n', length(poids2));

%% 2. ANALYSE CAPTEUR PRESSION
fprintf('\n============================================================\n');
fprintf('ANALYSE CAPTEUR DE PRESSION\n');
fprintf('============================================================\n');

% Régression linéaire
coeffs = polyfit(tension_V, pression_mmHg, 1);
a = coeffs(1);
b = coeffs(2);
fprintf('\n📈 Modèle: Pression = %.2f × Tension + %.2f\n', a, b);

% Prédictions
pression_pred = a * tension_V + b;

% Métriques
residus = pression_mmHg - pression_pred;
r2 = 1 - sum(residus.^2) / sum((pression_mmHg - mean(pression_mmHg)).^2);
mae = mean(abs(residus));
rmse = sqrt(mean(residus.^2));

fprintf('\n📊 Qualité du modèle:\n');
fprintf('   R² = %.6f\n', r2);
fprintf('   Erreur moyenne = %.2f mmHg\n', mae);
fprintf('   RMSE = %.2f mmHg\n', rmse);
fprintf('   Sensibilité = %.2f mmHg/V (%.4f mmHg/mV)\n', a, a/1000);

%% 3. ANALYSE CAPTEUR FORCE
fprintf('\n============================================================\n');
fprintf('ANALYSE CAPTEUR DE FORCE\n');
fprintf('============================================================\n');

% Gamme 1
coeffs1 = polyfit(tension1, poids1, 1);
a1 = coeffs1(1);
b1 = coeffs1(2);
fprintf('\n📈 Gamme 1 (Gain=10000): Poids = %.1f × Tension + %.2f\n', a1, b1);

% Gamme 2
coeffs2 = polyfit(tension2, poids2, 1);
a2 = coeffs2(1);
b2 = coeffs2(2);
fprintf('📈 Gamme 2 (Gain=1000): Poids = %.1f × Tension + %.2f\n', a2, b2);

%% 4. TEST DES FONCTIONS
fprintf('\n============================================================\n');
fprintf('TEST DES FONCTIONS\n');
fprintf('============================================================\n');

test_V = 0.200;
p_calc = a * test_V + b;
fprintf('\n🔹 Tension = %.0f mV → Pression = %.1f mmHg\n', test_V*1000, p_calc);

poids_calc1 = a1 * 0.3 + b1;
fprintf('🔹 Tension = 0.3 V (Gain=10000) → Poids = %.1f g\n', poids_calc1);

poids_calc2 = a2 * 3.4 + b2;
fprintf('🔹 Tension = 3.4 V (Gain=1000) → Poids = %.1f g\n', poids_calc2);

%% 5. VISUALISATION
fprintf('\n📊 Génération des graphiques...\n');

figure('Position', [100, 100, 1200, 800]);

% Capteur pression
subplot(2,2,1);
plot(tension_mV, pression_mmHg, 'ro', 'MarkerSize', 8, 'LineWidth', 2);
hold on;
tension_fine = linspace(min(tension_V), max(tension_V), 100);
plot(tension_fine*1000, a*tension_fine + b, 'b-', 'LineWidth', 2);
xlabel('Tension (mV)');
ylabel('Pression (mmHg)');
title('Capteur de pression - Étalonnage');
grid on;
legend('Mesures', 'Régression', 'Location', 'northwest');

% Résidus
subplot(2,2,2);
stem(tension_mV, residus, 'r', 'LineWidth', 2);
hold on;
plot([min(tension_mV), max(tension_mV)], [0,0], 'k-');
xlabel('Tension (mV)');
ylabel('Erreur (mmHg)');
title(sprintf('Résidus - MAE = %.2f mmHg', mae));
grid on;

% Capteur force
subplot(2,2,3);
plot(tension1, poids1, 'bo', 'MarkerSize', 8, 'LineWidth', 2);
hold on;
plot(tension2, poids2, 'go', 'MarkerSize', 8, 'LineWidth', 2);
tension_fine1 = linspace(min(tension1), max(tension1), 50);
tension_fine2 = linspace(min(tension2), max(tension2), 50);
plot(tension_fine1, a1*tension_fine1 + b1, 'b--', 'LineWidth', 2);
plot(tension_fine2, a2*tension_fine2 + b2, 'g--', 'LineWidth', 2);
xlabel('Tension (V)');
ylabel('Poids (g)');
title('Capteur de force - Deux gammes');
grid on;
legend('Gain=10000', 'Gain=1000', 'Location', 'northwest');

% Régression vs interpolation
subplot(2,2,4);
plot(tension_mV, pression_mmHg, 'ro', 'MarkerSize', 8, 'LineWidth', 2);
hold on;
plot(tension_fine*1000, a*tension_fine + b, 'b-', 'LineWidth', 2);
plot(tension_fine*1000, interp1(tension_V, pression_mmHg, tension_fine, 'linear'), ...
     'g--', 'LineWidth', 2);
xlabel('Tension (mV)');
ylabel('Pression (mmHg)');
title('Régression vs Interpolation');
grid on;
legend('Mesures', 'Régression', 'Interpolation', 'Location', 'northwest');

% Sauvegarde
figures_dir = fullfile(project_root, 'figures');
if ~exist(figures_dir, 'dir')
    mkdir(figures_dir);
end
saveas(gcf, fullfile(figures_dir, 'etalonnage_capteurs_matlab.png'));
fprintf('✅ Graphiques sauvegardés\n');