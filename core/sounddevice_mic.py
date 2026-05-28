import speech_recognition as sr
import sounddevice as sd
import queue

class SoundDeviceMicrophone(sr.AudioSource):
    """
    A PyAudio-free custom microphone class for SpeechRecognition using sounddevice.
    It streams audio chunks into a queue in a background thread and exposes a MockStream
    that SpeechRecognition's Recognizer can read from.
    """
    def __init__(self, device=None, sample_rate=16000, chunk_size=1024):
        self.device = device
        self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self.SAMPLE_WIDTH = 2  # 16-bit audio = 2 bytes per sample
        
        # If device is None, query the default system input device index
        if self.device is None:
            try:
                self.device = sd.default.device[0]
            except Exception:
                self.device = 0

        # Query the exact default sample rate of the chosen device
        try:
            device_info = sd.query_devices(self.device, 'input')
            self.SAMPLE_RATE = int(device_info['default_samplerate'])
            self.device_name = device_info['name']
        except Exception as e:
            print(f"[SoundDeviceMic] Error querying device {self.device}: {e}")
            self.device_name = "Unknown Microphone"
            if self.SAMPLE_RATE is None:
                self.SAMPLE_RATE = 16000

        self.audio_queue = queue.Queue()
        self._stream = None
        self.stream_mock = None

    def __enter__(self):
        print(f"[SoundDeviceMic] Starting stream on device: {self.device_name} (Index: {self.device}) at {self.SAMPLE_RATE}Hz")
        
        # Start sounddevice InputStream in background
        self._stream = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.SAMPLE_RATE,
            blocksize=self.CHUNK,
            dtype='int16',
            callback=self._callback
        )
        self._stream.start()
        
        # Mock class containing the read() interface for SpeechRecognition's listen loop
        class MockStream:
            def __init__(self, q):
                self.q = q
            def read(self, size):
                frames = []
                needed_bytes = size * 2
                bytes_accumulated = 0
                while bytes_accumulated < needed_bytes:
                    try:
                        # Wait for audio chunks from callback
                        chunk = self.q.get(timeout=1.0)
                        frames.append(chunk)
                        bytes_accumulated += len(chunk)
                    except queue.Empty:
                        break
                return b"".join(frames)[:needed_bytes]
                
        self.stream_mock = MockStream(self.audio_queue)
        return self

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[SoundDeviceMic] Stream status: {status}")
        # Put raw bytes of the int16 numpy array into our queue
        self.audio_queue.put(indata.tobytes())

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"[SoundDeviceMic] Stopping stream on device: {self.device_name}")
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    @property
    def stream(self):
        return self.stream_mock

    @stream.setter
    def stream(self, val):
        self.stream_mock = val
