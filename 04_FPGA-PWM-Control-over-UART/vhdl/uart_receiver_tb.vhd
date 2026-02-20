library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity uart_receiver_tb is
end uart_receiver_tb;

architecture Behavioral of uart_receiver_tb is
    constant CLK_PERIOD : time := 83.333 ns;
    constant BIT_TIME : time := 104 * CLK_PERIOD;
    
    signal clk : std_logic := '0';
    signal rst : std_logic := '1';
    signal rx : std_logic := '1';
    signal data : std_logic_vector(7 downto 0);
    signal data_valid : std_logic;
    
    component uart_receiver
        port(
            clk : in std_logic;
            rst : in std_logic;
            rx : in std_logic;
            data : out std_logic_vector(7 downto 0);
            data_valid : out std_logic
        );
    end component;
    
begin
    uut: uart_receiver
        port map(
            clk => clk,
            rst => rst,
            rx => rx,
            data => data,
            data_valid => data_valid
        );
    
    clk_process: process
    begin
        wait for CLK_PERIOD/2;
        clk <= not clk;
    end process;
    
    stim_proc: process
    begin
        wait for 1000 ns;
        rst <= '0';
        wait for 1000 ns;
        
        rx <= '0'; wait for BIT_TIME;
        rx <= '1'; wait for BIT_TIME;
        rx <= '0'; wait for BIT_TIME;
        rx <= '1'; wait for BIT_TIME;
        rx <= '0'; wait for BIT_TIME;
        rx <= '1'; wait for BIT_TIME;
        rx <= '0'; wait for BIT_TIME;
        rx <= '1'; wait for BIT_TIME;
        rx <= '1'; wait for BIT_TIME;
        
        wait for BIT_TIME * 10;
        
        assert false report "Test: OK" severity note;
        wait;
    end process;
    
end Behavioral;