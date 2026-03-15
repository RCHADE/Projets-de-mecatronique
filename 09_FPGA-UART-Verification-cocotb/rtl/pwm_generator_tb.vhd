library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity pwm_generator_tb is
end pwm_generator_tb;

architecture Behavioral of pwm_generator_tb is
    constant CLK_PERIOD : time := 83.333 ns;
    
    signal clk : std_logic := '0';
    signal rst : std_logic := '1';
    signal duty_cycle : std_logic_vector(6 downto 0) := (others => '0');
    signal pwm_out : std_logic;
    
    component pwm_generator
        port(
            clk : in std_logic;
            rst : in std_logic;
            duty_cycle : in std_logic_vector(6 downto 0);
            pwm_out : out std_logic
        );
    end component;
    
begin
    uut: pwm_generator
        port map(
            clk => clk,
            rst => rst,
            duty_cycle => duty_cycle,
            pwm_out => pwm_out
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
        
        duty_cycle <= "0011001"; -- 25
        wait for 100 us;
        
        duty_cycle <= "0110010"; -- 50
        wait for 100 us;
        
        duty_cycle <= "1001011"; -- 75
        wait for 100 us;
        
        assert false report "Test: OK" severity note;
        wait;
    end process;
    
end Behavioral;