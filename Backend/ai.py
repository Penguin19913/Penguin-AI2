import asyncio
from Backend.SpeechToText import SpeechRecognition
from Backend.Automation import Automation


async def listen_and_execute_loop(pause_after=0.5):
    """Continuously listen, then execute the transcribed command(s).

    - SpeechRecognition is blocking, so we call it with asyncio.to_thread.
    - After each transcription, we await Automation([...]) to run parsed commands.
    - pause_after: seconds to sleep when an error occurs to avoid tight loop.
    """
    # Create an event to signal cancellation
    stop_event = asyncio.Event()

    print("Starting continuous listen -> execute loop. Press Ctrl+C to stop.")
    
    # Return the stop_event so it can be accessed from outside
    return_event = asyncio.Event()

    while not return_event.is_set():
        try:
            print("Listening...")
            # run blocking recognition in a thread
            text = await asyncio.to_thread(SpeechRecognition)

            if not text:
                # nothing transcribed, continue listening
                await asyncio.sleep(0.1)
                # Check if we should stop
                if return_event.is_set():
                    break
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


# Event to control the listening loop
stop_event = None
loop = None

def start_listening():
    """Start the listening loop when called (e.g. from a button press)"""
    global stop_event, loop
    stop_event = asyncio.Event()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(listen_and_execute_loop())
    finally:
        loop.close()

def stop_listening():
    """Stop the listening loop"""
    global stop_event, loop
    if stop_event and loop:
        stop_event.set()
        # Cancel all running tasks
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.stop()
        return True
    return False

if __name__ == "__main__":
    # Only run directly if script is run directly (for testing)
    start_listening()