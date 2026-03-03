--------------------------------------------------------------------------------
-- 8-bit Integer MAC Unit
-- Performs: result = a * b + c
-- All inputs/outputs are 8-bit signed integers
--------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity mac_int8 is
    Port (
        clk     : in  STD_LOGIC;
        rst     : in  STD_LOGIC;
        a       : in  STD_LOGIC_VECTOR(7 downto 0);
        b       : in  STD_LOGIC_VECTOR(7 downto 0);
        c       : in  STD_LOGIC_VECTOR(7 downto 0);
        result  : out STD_LOGIC_VECTOR(15 downto 0);
        valid   : out STD_LOGIC
    );
end mac_int8;

architecture Behavioral of mac_int8 is
    signal a_reg, b_reg, c_reg : signed(7 downto 0);
    signal mult_result : signed(15 downto 0);
    signal acc_result  : signed(15 downto 0);
    signal valid_reg   : STD_LOGIC := '0';
begin

    process(clk, rst)
    begin
        if rst = '1' then
            a_reg <= (others => '0');
            b_reg <= (others => '0');
            c_reg <= (others => '0');
            mult_result <= (others => '0');
            acc_result <= (others => '0');
            result <= (others => '0');
            valid_reg <= '0';
            
        elsif rising_edge(clk) then
            -- Pipeline stage 1: Input registration
            a_reg <= signed(a);
            b_reg <= signed(b);
            c_reg <= signed(c);
            
            -- Pipeline stage 2: Multiplication
            mult_result <= a_reg * b_reg;
            
            -- Pipeline stage 3: Accumulation
            acc_result <= mult_result + resize(c_reg, 16);
            result <= STD_LOGIC_VECTOR(acc_result);
            
            -- Valid signal (3 cycle latency)
            valid_reg <= not rst;
        end if;
    end process;
    
    valid <= valid_reg;

end Behavioral;