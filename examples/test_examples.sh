#!/bin/bash
# Script de teste para Polly
# Execute após instalar: bash examples/test_examples.sh

echo "🌸 Testando Polly - AI Assistant"
echo "================================"
echo ""

# Test 1: Version
echo "1️⃣  Testando versão..."
polly --version
echo ""

# Test 2: List models
echo "2️⃣  Listando modelos disponíveis..."
polly --list-models
echo ""

# Test 3: Simple query
echo "3️⃣  Pergunta simples..."
polly "O que é recursão em programação?"
echo ""

# Test 4: Command mode
echo "4️⃣  Modo comando (apenas comando)..."
polly -c "listar todos os arquivos Python no diretório atual"
echo ""

# Test 5: Command explain mode
echo "5️⃣  Modo comando com explicação..."
polly -ce "encontrar arquivos modificados nas últimas 24 horas"
echo ""

# Test 6: Explain file
echo "6️⃣  Explicar arquivo..."
echo "print('Hello World')" > /tmp/test_polly.py
polly -e /tmp/test_polly.py
rm /tmp/test_polly.py
echo ""

# Test 7: Pipe test
echo "7️⃣  Teste com pipe..."
echo "def factorial(n): return 1 if n == 0 else n * factorial(n-1)" | polly -e
echo ""

# Test 8: Debug mode
echo "8️⃣  Modo debug..."
echo "bash: command not found: pytohn" | polly -d
echo ""

# Test 9: Different model
echo "9️⃣  Testando modelo diferente (openai)..."
polly --model openai "Explique Docker em uma frase"
echo ""

# Test 10: Temperature
echo "🔟 Testando com temperatura alta (criativo)..."
polly --temperature 1.5 "Escreva um haiku sobre Linux"
echo ""

echo "✅ Testes concluídos!"
echo ""
echo "Para testar modo interativo, execute:"
echo "  polly -i"
