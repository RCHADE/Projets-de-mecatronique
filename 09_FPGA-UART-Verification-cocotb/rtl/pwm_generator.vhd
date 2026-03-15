library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity pwm_generator is
    port(
        clk : in std_logic;
        rst : in std_logic;
        duty_cycle : in std_logic_vector(6 downto 0);
        pwm_out : out std_logic
    );
end pwm_generator;

architecture Behavioral of pwm_generator is
    constant COUNTER_MAX : integer := 100;
    signal counter : integer range 0 to 99 := 0;
    signal duty_int : integer range 0 to 100;
    
begin
    duty_int <= to_integer(unsigned(duty_cycle));
    
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                counter <= 0;
                pwm_out <= '0';
            else
                if counter = COUNTER_MAX - 1 then
                    counter <= 0;
                else
                    counter <= counter + 1;
                end if;
                
                if counter < duty_int then
                    pwm_out <= '1';
                else
                    pwm_out <= '0';
                end if;
            end if;
        end if;
    end process;
end Behavioral;