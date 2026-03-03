#!/bin/bash

echo "========================================="
echo "Simulation des differents formats MAC"
echo "========================================="

# Creer le dossier resultats s'il n'existe pas
mkdir -p resultats

# Nettoyer les anciens fichiers
rm -f *.o *.cf work-obj*.cf

echo ""
echo "1. Simulation INT8..."
ghdl -a --ieee=synopsys -fexplicit src/mac_int8.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation INT8"
    exit 1
fi

ghdl -a --ieee=synopsys -fexplicit sim/tb_mac_int8.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation testbench INT8"
    exit 1
fi

ghdl -e tb_mac_int8
if [ $? -eq 0 ]; then
    echo "Execution INT8..."
    ghdl -r tb_mac_int8
else
    echo "Erreur elaboration INT8"
    exit 1
fi

echo ""
echo "2. Simulation Fixed16..."
ghdl -a --ieee=synopsys -fexplicit src/mac_fixed16.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation Fixed16"
    exit 1
fi

ghdl -a --ieee=synopsys -fexplicit sim/tb_mac_fixed16.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation testbench Fixed16"
    exit 1
fi

ghdl -e tb_mac_fixed16
if [ $? -eq 0 ]; then
    echo "Execution Fixed16..."
    ghdl -r tb_mac_fixed16
else
    echo "Erreur elaboration Fixed16"
    exit 1
fi

echo ""
echo "3. Simulation Float16..."
ghdl -a --ieee=synopsys -fexplicit src/mac_float16.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation Float16"
    exit 1
fi

ghdl -a --ieee=synopsys -fexplicit sim/tb_mac_float16.vhd
if [ $? -ne 0 ]; then
    echo "Erreur compilation testbench Float16"
    exit 1
fi

ghdl -e tb_mac_float16
if [ $? -eq 0 ]; then
    echo "Execution Float16..."
    ghdl -r tb_mac_float16
else
    echo "Erreur elaboration Float16"
    exit 1
fi

echo ""
echo "========================================="
echo "Simulations terminees"
echo "========================================="
echo ""
echo "Fichiers generes dans le dossier resultats/ :"
ls -la resultats/
echo ""
echo "Pour analyser les resultats :"
echo "  cd python"
echo "  python3 mac_analysis.py"