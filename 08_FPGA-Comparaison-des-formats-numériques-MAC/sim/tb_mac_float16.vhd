--------------------------------------------------------------------------------
-- Testbench for 16-bit Floating-Point MAC
--------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_mac_float16 is
end tb_mac_float16;

architecture Behavioral of tb_mac_float16 is
    component mac_float16 is
        Port (
            clk     : in  STD_LOGIC;
            rst     : in  STD_LOGIC;
            a       : in  STD_LOGIC_VECTOR(15 downto 0);
            b       : in  STD_LOGIC_VECTOR(15 downto 0);
            c       : in  STD_LOGIC_VECTOR(15 downto 0);
            result  : out STD_LOGIC_VECTOR(15 downto 0);
            valid   : out STD_LOGIC
        );
    end component;
    
    signal clk      : STD_LOGIC := '0';
    signal rst      : STD_LOGIC := '1';
    signal a, b, c  : STD_LOGIC_VECTOR(15 downto 0) := (others => '0');
    signal result   : STD_LOGIC_VECTOR(15 downto 0);
    signal valid    : STD_LOGIC;
    
    file results_file : text open write_mode is "./resultats/float16_results.csv";
    constant clk_period : time := 10 ns;
    
begin
    uut: mac_float16 port map (
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
    begin
        write(v_line, string'("a,b,c,result,valid"));
        writeline(results_file, v_line);
        
        rst <= '1';
        wait for 100 ns;
        rst <= '0';
        wait for clk_period;
        
        -- Simple test patterns
        for i in 1 to 20 loop
            a <= STD_LOGIC_VECTOR(to_signed(i * 100, 16));
            b <= STD_LOGIC_VECTOR(to_signed(i * 50, 16));
            c <= STD_LOGIC_VECTOR(to_signed(i * 25, 16));
            
            wait for clk_period * 4;
            
            if valid = '1' then
                write(v_line, integer'image(i) & ",");
                write(v_line, integer'image(i*2) & ",");
                write(v_line, integer'image(i*3) & ",");
                write(v_line, integer'image(to_integer(signed(result))) & ",");
                write(v_line, string'("1"));
                writeline(results_file, v_line);
            end if;
            
            wait for clk_period;
        end loop;
        
        wait;
    end process;

end Behavioral;