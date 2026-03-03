--------------------------------------------------------------------------------
-- Testbench for 8-bit Integer MAC
--------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_mac_int8 is
end tb_mac_int8;

architecture Behavioral of tb_mac_int8 is
    -- Component declaration
    component mac_int8 is
        Port (
            clk     : in  STD_LOGIC;
            rst     : in  STD_LOGIC;
            a       : in  STD_LOGIC_VECTOR(7 downto 0);
            b       : in  STD_LOGIC_VECTOR(7 downto 0);
            c       : in  STD_LOGIC_VECTOR(7 downto 0);
            result  : out STD_LOGIC_VECTOR(15 downto 0);
            valid   : out STD_LOGIC
        );
    end component;
    
    -- Signals
    signal clk      : STD_LOGIC := '0';
    signal rst      : STD_LOGIC := '1';
    signal a, b, c  : STD_LOGIC_VECTOR(7 downto 0) := (others => '0');
    signal result   : STD_LOGIC_VECTOR(15 downto 0);
    signal valid    : STD_LOGIC;
    
    -- Test vectors
    type test_vector is record
        a_val : integer;
        b_val : integer;
        c_val : integer;
        expected : integer;
    end record;
    
    type test_array is array (0 to 9) of test_vector;
    
    constant test_vectors : test_array := (
        (a_val => 10, b_val => 20, c_val => 5, expected => 205),   -- 10*20+5 = 205
        (a_val => -10, b_val => 20, c_val => 5, expected => -195),  -- -10*20+5 = -195
        (a_val => 127, b_val => 127, c_val => 127, expected => 16256), -- 127*127+127 = 16256
        (a_val => -128, b_val => -128, c_val => -128, expected => 16256), -- (-128)*(-128)-128 = 16256
        (a_val => 0, b_val => 50, c_val => 25, expected => 25),
        (a_val => 1, b_val => 1, c_val => 1, expected => 2),
        (a_val => -1, b_val => -1, c_val => -1, expected => 0),
        (a_val => 15, b_val => 3, c_val => -10, expected => 35),
        (a_val => -50, b_val => 2, c_val => 100, expected => 0),
        (a_val => 7, b_val => 8, c_val => -56, expected => 0)
    );
    
    -- File output
    file results_file : text open write_mode is "./resultats/int8_results.csv";
    
    -- Clock period
    constant clk_period : time := 10 ns;
    
begin
    -- Instantiate DUT
    uut: mac_int8 port map (
        clk => clk,
        rst => rst,
        a => a,
        b => b,
        c => c,
        result => result,
        valid => valid
    );
    
    -- Clock generation
    clk <= not clk after clk_period/2;
    
    -- Stimulus process
    process
        variable v_line : line;
        variable v_error_count : integer := 0;
        variable v_expected_signed : signed(15 downto 0);
        variable v_result_signed : signed(15 downto 0);
    begin
        -- Write CSV header
        write(v_line, string'("a,b,c,expected,actual,error,valid"));
        writeline(results_file, v_line);
        
        -- Reset
        rst <= '1';
        wait for 100 ns;
        rst <= '0';
        wait for clk_period;
        
        -- Apply test vectors
        for i in test_vectors'range loop
            a <= STD_LOGIC_VECTOR(to_signed(test_vectors(i).a_val, 8));
            b <= STD_LOGIC_VECTOR(to_signed(test_vectors(i).b_val, 8));
            c <= STD_LOGIC_VECTOR(to_signed(test_vectors(i).c_val, 8));
            
            wait for clk_period * 4;  -- Wait for pipeline to fill
            
            -- Check result when valid
            if valid = '1' then
                v_expected_signed := to_signed(test_vectors(i).expected, 16);
                v_result_signed := signed(result);
                
                -- Write to CSV
                write(v_line, integer'image(test_vectors(i).a_val) & ",");
                write(v_line, integer'image(test_vectors(i).b_val) & ",");
                write(v_line, integer'image(test_vectors(i).c_val) & ",");
                write(v_line, integer'image(test_vectors(i).expected) & ",");
                write(v_line, integer'image(to_integer(v_result_signed)) & ",");
                
                if v_result_signed = v_expected_signed then
                    write(v_line, string'("0,"));
                else
                    write(v_line, string'("1,"));
                    v_error_count := v_error_count + 1;
                end if;
                
                write(v_line, string'("1"));
                writeline(results_file, v_line);
            end if;
            
            wait for clk_period;
        end loop;
        
        -- Summary
        write(v_line, string'("# TOTAL ERRORS: " & integer'image(v_error_count)));
        writeline(results_file, v_line);
        
        wait;
    end process;

end Behavioral;