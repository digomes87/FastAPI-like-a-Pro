#!/usr/bin/env python3
"""Script para testar validação de senha específica."""

from fast_zero.password_validator import password_validator, PasswordValidationError

def test_password(password: str):
    """Testa uma senha específica contra o validador."""
    print(f"Testando senha: '{password}'")
    print(f"Comprimento: {len(password)} caracteres")
    print()
    
    try:
        password_validator.validate(password)
        print("✅ Senha VÁLIDA - passou em todas as validações!")
    except PasswordValidationError as e:
        print("❌ Senha INVÁLIDA:")
        print(f"Mensagem: {e.message}")
        print("Erros encontrados:")
        for i, error in enumerate(e.errors, 1):
            print(f"  {i}. {error}")
    
    print()
    score = password_validator.get_strength_score(password)
    print(f"Score de força da senha: {score}/100")

if __name__ == "__main__":
    # Senha fornecida pelo usuário
    test_password("cerna6-qowziW-hetjyf")