--------------------------------------------------------------------------------
-- Testbench for 16-bit Fixed-Point MAC
--------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_mac_fixed16 is
end tb_mac_fixed16;

architecture Behavioral of tb_mac_fixed16 is
    component mac_fixed16 is
        Port (
            clk     : in  STD_LOGIC;
            rst     : in  STD_LOGIC;
            a       : in  STD_LOGIC_VECTOR(15 downto 0);
            b       : in  STD_LOGIC_VECTOR(15 downto 0);
            c       : in  STD_LOGIC_VECTOR(15 downto 0);
            result  : out STD_LOGIC_VECTOR(31 downto 0);
            valid   : out STD_LOGIC
        );
    end component;
    
    signal clk      : STD_LOGIC := '0';
    signal rst      : STD_LOGIC := '1';
    signal a, b, c  : STD_LOGIC_VECTOR(15 downto 0) := (others => '0');
    signal result   : STD_LOGIC_VECTOR(31 downto 0);
    signal valid    : STD_LOGIC;
    
    -- File output
    file results_file : text open write_mode is "./resultats/fixed16_results.csv";
    
    constant clk_period : time := 10 ns;
    
    -- Function to convert float to Q8.8 fixed point
    function to_fixed16(val : real) return STD_LOGIC_VECTOR is
        variable int_val : integer;
    begin
        int_val := integer(val * 256.0);
        return STD_LOGIC_VECTOR(to_signed(int_val, 16));
    end function;
    
    -- Function to convert Q8.8 fixed point to float
    function to_float(val : signed(31 downto 0)) return real is
    begin
        return real(to_integer(val)) / 256.0;
    end function;
    
begin
    uut: mac_fixed16 port map (
        clk => clk,
        rst => rst,
        a => a,
        b => b,
        c => c,
        result => result,
        valid => valid
    );
    
    clk <= not clk after clk_period/2;
    
    process
        variable v_line : line;
        variable v_a_float, v_b_float, v_c_float, v_expected_float : real;
        variable v_error_count : integer := 0;
        variable v_error_mse : real := 0.0;
    begin
        -- Write CSV header
        write(v_line, string'("a,b,c,expected,actual,error_percent,valid"));
        writeline(results_file, v_line);
        
        rst <= '1';
        wait for 100 ns;
        rst <= '0';
        wait for clk_period;
        
        -- Test cases with fractional values
        for i in 1 to 20 loop
            -- Generate test values (range -10 to 10 with fractions)
            v_a_float := real((i mod 20) - 10) + real(i mod 10) / 10.0;
            v_b_float := real(((i+5) mod 20) - 10) + real((i+3) mod 10) / 10.0;
            v_c_float := real(((i+10) mod 20) - 10) + real((i+7) mod 10) / 10.0;
            
            a <= to_fixed16(v_a_float);
            b <= to_fixed16(v_b_float);
            c <= to_fixed16(v_c_float);
            v_expected_float := v_a_float * v_b_float + v_c_float;
            
            wait for clk_period * 4;
            
            if valid = '1' then
                write(v_line, real'image(v_a_float) & ",");
                write(v_line, real'image(v_b_float) & ",");
                write(v_line, real'image(v_c_float) & ",");
                write(v_line, real'image(v_expected_float) & ",");
                write(v_line, real'image(to_float(signed(result))) & ",");
                
                -- Calculate error
                write(v_line, real'image(100.0 * abs(to_float(signed(result)) - v_expected_float) / abs(v_expected_float)) & ",");
                write(v_line, string'("1"));
                writeline(results_file, v_line);
            end if;
            
            wait for clk_period;
        end loop;
        
        wait;
    end process;

end Behavioral;