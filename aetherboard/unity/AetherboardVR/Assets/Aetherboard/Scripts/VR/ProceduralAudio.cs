using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Runtime procedural waveform synthesis — no audio assets required.
    /// </summary>
    public static class ProceduralAudio
    {
        private const int SampleRate = 44100;

        public static AudioClip CreateTone(float frequency, float duration, float volume)
        {
            var samples = Mathf.CeilToInt(SampleRate * duration);
            var data = new float[samples];
            for (var i = 0; i < samples; i++)
            {
                var t = i / (float)SampleRate;
                var env = Envelope(t, duration);
                data[i] = Mathf.Sin(2f * Mathf.PI * frequency * t) * volume * env;
            }
            return BuildClip("tone", data);
        }

        public static AudioClip CreateChord(float[] frequencies, float duration, float volume)
        {
            if (frequencies == null || frequencies.Length == 0)
                return CreateTone(440f, duration, volume);

            var samples = Mathf.CeilToInt(SampleRate * duration);
            var data = new float[samples];
            for (var i = 0; i < samples; i++)
            {
                var t = i / (float)SampleRate;
                var env = Envelope(t, duration);
                var sum = 0f;
                foreach (var freq in frequencies)
                    sum += Mathf.Sin(2f * Mathf.PI * freq * t);
                data[i] = sum / frequencies.Length * volume * env;
            }
            return BuildClip("chord", data);
        }

        public static AudioClip CreateSweep(float fromHz, float toHz, float duration, float volume)
        {
            var samples = Mathf.CeilToInt(SampleRate * duration);
            var data = new float[samples];
            for (var i = 0; i < samples; i++)
            {
                var t = i / (float)SampleRate;
                var env = Envelope(t, duration);
                var ratio = t / duration;
                var freq = Mathf.Lerp(fromHz, toHz, ratio);
                data[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * volume * env;
            }
            return BuildClip("sweep", data);
        }

        public static AudioClip CreateNoiseBurst(float duration, float volume)
        {
            var samples = Mathf.CeilToInt(SampleRate * duration);
            var data = new float[samples];
            for (var i = 0; i < samples; i++)
            {
                var t = i / (float)SampleRate;
                var env = Envelope(t, duration, 0.02f);
                data[i] = (Random.value * 2f - 1f) * volume * env;
            }
            return BuildClip("noise", data);
        }

        private static float Envelope(float t, float duration, float attack = 0.01f)
        {
            var release = Mathf.Max(attack, duration * 0.35f);
            if (t < attack) return t / attack;
            if (t > duration - release) return Mathf.Clamp01((duration - t) / release);
            return 1f;
        }

        private static AudioClip BuildClip(string name, float[] data)
        {
            var clip = AudioClip.Create(name, data.Length, 1, SampleRate, false);
            clip.SetData(data, 0);
            return clip;
        }
    }
}
