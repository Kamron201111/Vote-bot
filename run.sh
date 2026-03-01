#!/bin/bash
# Ikkala botni ham bir vaqtda ishga tushirish

echo "🚀 Botlar ishga tushirilmoqda..."

# Asosiy bot fonda ishlaydi
python3 main.py &
MAIN_PID=$!
echo "✅ Asosiy bot ishga tushdi (PID: $MAIN_PID)"

# Admin bot fonda ishlaydi
python3 admin.py &
ADMIN_PID=$!
echo "✅ Admin bot ishga tushdi (PID: $ADMIN_PID)"

echo ""
echo "📌 Botlarni to'xtatish uchun: kill $MAIN_PID $ADMIN_PID"
echo "📌 Yoki: pkill -f 'python3 main.py' && pkill -f 'python3 admin.py'"

# Ikkalasini kutish
wait
