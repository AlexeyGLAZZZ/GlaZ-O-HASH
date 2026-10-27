import random

RU_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
EN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"

def get_alphabet_by_marker(marker_digit):
    if marker_digit % 2 == 0:
        return RU_ALPHABET
    else:
        return EN_ALPHABET

def shift_char(ch, shift, alphabet):
    idx = alphabet.index(ch)
    new_idx = (idx + shift) % len(alphabet)
    return alphabet[new_idx]

def encrypt_variable_caesar(text):
    encrypted_chars = []
    
    letter_shifts = []  
    digit_shifts = []   
    
    has_ru = any(ch in RU_ALPHABET for ch in text)
    target_lang = "RU" if has_ru else "EN"
    alphabet = RU_ALPHABET if target_lang == "RU" else EN_ALPHABET
    
    for ch in text:
        if ch in alphabet:
            shift = random.randint(0, len(alphabet) - 1)
            letter_shifts.append(shift)
            encrypted_chars.append(shift_char(ch, shift, alphabet))
            
        elif ch in DIGITS:
            original_digit = int(ch)
            shift = random.randint(0, 99)
            digit_shifts.append(shift)
            
            new_digit_val = (original_digit + shift) % 10
            encrypted_chars.append(str(new_digit_val))
            
        else:
            encrypted_chars.append(ch)

    encrypted_text = "".join(encrypted_chars)
    
    
    obf_letter_parts = []
    for s in letter_shifts:
        s_str = f"{s:02d}"       
        obfuscated = s_str[1] + s_str[0] 
        obf_letter_parts.append(obfuscated)
    obf_letters_str = "".join(obf_letter_parts)
    
    obf_digit_parts = []
    for d in digit_shifts:
        d_str = f"{d:02d}"
        obf = d_str[1] + d_str[0]
        obf_digit_parts.append(obf)
    obf_digits_str = "".join(obf_digit_parts)
    
    if target_lang == "RU":
        marker = random.choice([0, 2, 4, 6, 8])
    else:
        marker = random.choice([1, 3, 5, 7, 9])
    
    final_key = f"{obf_letters_str}#{obf_digits_str}#{marker}"
    
    return encrypted_text, final_key, letter_shifts, digit_shifts

def parse_key(final_key_str):
    parts = final_key_str.split('#')
    if len(parts) != 3:
        raise ValueError("Неверный формат ключа")
    
    obf_letters = parts[0]
    obf_digits = parts[1]
    marker_str = parts[2]
    
    if not marker_str.isdigit() or len(marker_str) != 1:
        raise ValueError("Маркер должен быть одной цифрой")
    marker = int(marker_str)
    
    real_letter_shifts = []
    if len(obf_letters) % 2 != 0:
        raise ValueError("Ошибка в части ключа для букв")
    for i in range(0, len(obf_letters), 2):
        pair = obf_letters[i:i+2]
        original = pair[1] + pair[0]
        real_letter_shifts.append(int(original))
        
    real_digit_shifts = []
    if len(obf_digits) % 2 != 0:
        raise ValueError("Ошибка в части ключа для цифр")
    for i in range(0, len(obf_digits), 2):
        pair = obf_digits[i:i+2]
        original = pair[1] + pair[0]
        real_digit_shifts.append(int(original))
        
    return real_letter_shifts, real_digit_shifts, marker

def decrypt_variable_caesar(encrypted_text, real_letter_shifts, real_digit_shifts, marker):
    alphabet = get_alphabet_by_marker(marker)
    decrypted_chars = []
    
    l_idx = 0
    d_idx = 0
    
    for ch in encrypted_text:
        if ch in alphabet:
            if l_idx >= len(real_letter_shifts):
                decrypted_chars.append(ch)
                continue
            
            shift = real_letter_shifts[l_idx]
            l_idx += 1
            decrypted_chars.append(shift_char(ch, -shift, alphabet))
            
        elif ch in DIGITS:
            if d_idx >= len(real_digit_shifts):
                decrypted_chars.append(ch)
                continue
                
            shift = real_digit_shifts[d_idx]
            d_idx += 1
            
            current_digit = int(ch)
            original = (current_digit - shift) % 10
            decrypted_chars.append(str(original))
            
        else:
            decrypted_chars.append(ch)
            
    return "".join(decrypted_chars)

def main():
    print("=== GlaZ-O-HASH ===")
    print("от 1 до 99 символов.")
    print()
    print("1 — Зашифровать и автопроверить")
    print("2 — Расшифровать вручную")
    choice = input("Ввод (1/2): ").strip()

    if choice == "1":
        text = input("Введите текст (буквы + цифры): ").upper()
        
        has_ru = any(ch in RU_ALPHABET for ch in text)
        has_en = any(ch in EN_ALPHABET for ch in text)
        
        if has_ru and has_en:
            print("⚠️ ВНИМАНИЕ: Смешанный язык! Будет выбран один маркер.")
            confirm = input("Продолжить? (да/нет): ").strip().lower()
            if confirm != 'да':
                return

        enc_text, final_key, _, _ = encrypt_variable_caesar(text)

        print("\n--- Результат ---")
        print(f"Шифротекст: {enc_text}")
        print(f"Ключ: {final_key}")
        
        try:
            l_shifts, d_shifts, marker = parse_key(final_key)
            dec_text = decrypt_variable_caesar(enc_text, l_shifts, d_shifts, marker)
            
            if dec_text == text:
                print("✅ Автопроверка: расшифровка полностью совпадает!")
            else:
                print("⚠️ Автопроверка: НЕ совпадает!")
                print(f"Оригинал:   {text}")
                print(f"Расшифровка:{dec_text}")
        except Exception as e:
            print(f"Ошибка при автопроверке: {e}")

    elif choice == "2":
        enc_text = input("Шифротекст: ").upper()
        final_key = input("Ключ (формат: буквы#цифры#маркер): ").strip()
        
        try:
            l_shifts, d_shifts, marker = parse_key(final_key)
            lang_name = "Русский" if marker % 2 == 0 else "Английский"
            
            dec_text = decrypt_variable_caesar(enc_text, l_shifts, d_shifts, marker)
            print("Расшифровка:")
            print(dec_text)
        except ValueError as e:
            print(f"Ошибка формата ключа: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()
