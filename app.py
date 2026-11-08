import os, telebot, ffmpeg, tempfile, threading

bot = telebot.TeleBot("9003851890:AAHT45jk_OV8TlyDLD1EfV24e22cXCTmN_4")
INSERT_VIDEO_PATH = "insert.mp4"

@bot.message_handler(content_types=['video'])
def handle_video(message):
    threading.Thread(target=process_video, args=(message,)).start()

def process_video(message):
    msg = bot.reply_to(message, "Скачиваю видео...")
    
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(downloaded)
            user_video = f.name

        bot.edit_message_text("Обрабатываю...", message.chat.id, msg.message_id)

        probe = ffmpeg.probe(user_video)
        duration = float(probe['format']['duration'])
        half = duration / 2

        part1 = ffmpeg.input(user_video, t=half)
        insert = ffmpeg.input(INSERT_VIDEO_PATH)
        part2 = ffmpeg.input(user_video, ss=half)
        
        joined = ffmpeg.concat(
            part1.video, part1.audio, 
            insert.video, insert.audio, 
            part2.video, part2.audio, 
            v=1, a=1
        ).node
        
        output = ffmpeg.output(
            joined[0], joined[1], "output.mp4",
            preset='ultrafast', threads=4
        )
        
        ffmpeg.run(output, overwrite_output=True)

        bot.edit_message_text("Отправляю!", message.chat.id, msg.message_id)
        with open("output.mp4", "rb") as vid:
            bot.send_video(message.chat.id, vid)
            
        os.remove(user_video)
        os.remove("output.mp4")

    except Exception as e:
        bot.edit_message_text(f"Ошибка: {str(e)}", message.chat.id, msg.message_id)

print("Бот запущен...")
bot.infinity_polling()
