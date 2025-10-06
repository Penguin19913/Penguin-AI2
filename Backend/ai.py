import asyncio
from SpeechToText import SpeechRecognition
from Automation import Automation


async def listen_and_execute_loop(pause_after=0.5):
    """Continuously listen, then execute the transcribed command(s).

    - SpeechRecognition is blocking, so we call it with asyncio.to_thread.
    - After each transcription, we await Automation([...]) to run parsed commands.
    - pause_after: seconds to sleep when an error occurs to avoid tight loop.
    """

    print("Starting continuous listen -> execute loop. Press Ctrl+C to stop.")

    while True:
        try:
            print("Listening...")
            # run blocking recognition in a thread
            text = await asyncio.to_thread(SpeechRecognition)

            if not text:
                # nothing transcribed, continue listening
                await asyncio.sleep(0.1)
                continue

            text = text.lower()
            print("Transcribed:", text)

            # pass the transcription into Automation which will parse/execute commands
            try:
                await Automation([text])
            except Exception as e:
                print(f"Automation error: {e}")

            # small pause to allow any resources to settle before next listen
            await asyncio.sleep(pause_after)

        except KeyboardInterrupt:
            print("Interrupted by user — stopping loop.")
            break
        except Exception as e:
            print(f"Error in listen loop: {e}")
            await asyncio.sleep(pause_after)


if __name__ == "__main__":
    asyncio.run(listen_and_execute_loop())