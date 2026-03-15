library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity uart_receiver is
    port(
        clk : in std_logic;
        rst : in std_logic;
        rx : in std_logic;
        data : out std_logic_vector(7 downto 0);
        data_valid : out std_logic
    );
end uart_receiver;

architecture Behavioral of uart_receiver is
    constant CLK_PER_BIT : integer := 104;
    
    type state_type is (IDLE, START, DATA, STOP);
    signal state : state_type := IDLE;
    signal clk_count : integer range 0 to 103 := 0;
    signal bit_index : integer range 0 to 7 := 0;
    signal rx_buffer : std_logic_vector(7 downto 0);
    
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                state <= IDLE;
                data_valid <= '0';
                clk_count <= 0;
                bit_index <= 0;
                rx_buffer <= (others => '0');
            else
                case state is
                    when IDLE =>
                        data_valid <= '0';
                        clk_count <= 0;
                        bit_index <= 0;
                        if rx = '0' then
                            state <= START;
                        end if;
                    
                    when START =>
                        if clk_count = (CLK_PER_BIT - 1)/2 then
                            if rx = '0' then
                                clk_count <= 0;
                                state <= DATA;
                            else
                                state <= IDLE;
                            end if;
                        else
                            clk_count <= clk_count + 1;
                        end if;
                    
                    when DATA =>
                        if clk_count = CLK_PER_BIT - 1 then
                            clk_count <= 0;
                            rx_buffer(bit_index) <= rx;
                            if bit_index = 7 then
                                state <= STOP;
                            else
                                bit_index <= bit_index + 1;
                            end if;
                        else
                            clk_count <= clk_count + 1;
                        end if;
                    
                    when STOP =>
                        if clk_count = CLK_PER_BIT - 1 then
                            data <= rx_buffer;
                            data_valid <= '1';
                            state <= IDLE;
                        else
                            clk_count <= clk_count + 1;
                        end if;
                end case;
            end if;
        end if;
    end process;
end Behavioral;