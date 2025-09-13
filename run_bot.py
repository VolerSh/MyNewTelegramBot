import asyncio
import sys

async def read_stream(stream, prefix):
    """Читает и выводит данные из потока (stdout/stderr) процесса."""
    while True:
        line = await stream.readline()
        if line:
            # Используем кодировку консоли по умолчанию и заменяем ошибки, чтобы избежать падения
            print(f"[{prefix}] {line.decode(sys.stdout.encoding, errors='replace').rstrip()}", flush=True)
        else:
            break

async def main():
    """
    Запускает бота как дочерний процесс и управляет им.
    """
    # Флаг -u важен для отключения буферизации вывода в дочернем процессе
    command = [sys.executable, "-u", "-m", "app.telegram_bot.bot"]
    
    print(f"Запуск дочернего процесса командой: {' '.join(command)}", flush=True)
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    print(f"Бот запущен как дочерний процесс с PID: {process.pid}", flush=True)

    # Асинхронно читаем stdout и stderr
    await asyncio.gather(
        read_stream(process.stdout, "BOT-STDOUT"),
        read_stream(process.stderr, "BOT-STDERR")
    )

    # Ждем завершения процесса
    await process.wait()
    print(f"Дочерний процесс с ботом завершился с кодом: {process.returncode}", flush=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nПолучен сигнал KeyboardInterrupt (Ctrl+C). Завершаю работу...", flush=True)
    finally:
        print("Программа завершена.", flush=True)
        # Находим и завершаем все оставшиеся задачи
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        
        # Собираем отмененные задачи
        group = asyncio.gather(*tasks, return_exceptions=True)
        loop.run_until_complete(group)
        loop.close()