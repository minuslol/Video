import os, telebot, ffmpeg, tempfile

# Вставь свой токен внутрь кавычек
bot = telebot.TeleBot("9003851890:AAHT45jk_OV8TlyDLD1EfV24e22cXCTmN_4")
INSERT_VIDEO_PATH = "insert.mp4"

@bot.message_handler(content_types=['video'])
def handle_video(message):
    msg = bot.reply_to(message, "Скачиваю видео...")
    
    try:
        # 1. Скачиваем видео
        file_info = bot.get_file(message.video.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(downloaded)
            user_video = f.name

        bot.edit_message_text("Обрабатываю... Это может занять время.", message.chat.id, msg.message_id)

        # 2. Считаем длительность и делим пополам
        probe = ffmpeg.probe(user_video)
        duration = float(probe['format']['duration'])
        half = duration / 2

        # 3. Склеиваем: первая половина + вставка + вторая половина
        part1 = ffmpeg.input(user_video, t=half)
        insert = ffmpeg.input(INSERT_VIDEO_PATH)
        part2 = ffmpeg.input(user_video, ss=half)
        
        # Склеиваем видео и аудио дорожки
        joined = ffmpeg.concat(
            part1.video, part1.audio, 
            insert.video, insert.audio, 
            part2.video, part2.audio, 
            v=1, a=1
        ).node
        
        output = ffmpeg.output(joined[0], joined[1], "output.mp4")
        ffmpeg.run(output, overwrite_output=True)

        # 4. Отправляем результат
        bot.edit_message_text("Отправляю готовое видео!", message.chat.id, msg.message_id)
        with open("output.mp4", "rb") as vid:
            bot.send_video(message.chat.id, vid)
            
        # Удаляем временные файлы, чтобы не забить память
        os.remove(user_video)
        os.remove("output.mp4")

    except Exception as e:
        bot.edit_message_text(f"Ошибка: {str(e)}", message.chat.id, msg.message_id)

print("Бот запущен...")
bot.infinity_polling()
