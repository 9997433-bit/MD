using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Procedural audio cues — no external assets required.
    /// </summary>
    [RequireComponent(typeof(AudioSource))]
    public class BattleAudioController : MonoBehaviour
    {
        private AudioSource _source;
        private BattleDirector _director;

        public void Bind(BattleDirector director)
        {
            _director = director;
            _source = GetComponent<AudioSource>();
            _source.playOnAwake = false;
            _source.spatialBlend = 0f;
            _director.OnPhaseChanged.AddListener(OnPhaseChanged);
            _director.OnLogAdded.AddListener(OnLog);
            _director.OnBattleEnded.AddListener(OnBattleEnded);
        }

        private void OnDestroy()
        {
            if (_director == null) return;
            _director.OnPhaseChanged.RemoveListener(OnPhaseChanged);
            _director.OnLogAdded.RemoveListener(OnLog);
            _director.OnBattleEnded.RemoveListener(OnBattleEnded);
        }

        private void OnPhaseChanged(BattlePhase phase)
        {
            PlayTone(phase switch
            {
                BattlePhase.Move => 440f,
                BattlePhase.Action => 523f,
                BattlePhase.Weave => 587f,
                BattlePhase.Resolve => 330f,
                _ => 0f
            }, 0.08f, 0.15f);
        }

        private void OnLog(string msg)
        {
            if (msg.Contains("伤害")) PlayTone(220f, 0.05f, 0.12f);
            else if (msg.Contains("治疗")) PlayTone(880f, 0.06f, 0.18f);
            else if (msg.Contains("打断")) PlayTone(1200f, 0.04f, 0.2f);
            else if (msg.Contains("预警")) PlayTone(180f, 0.1f, 0.25f);
            else if (msg.Contains("即死") || msg.Contains("倒下")) PlayTone(110f, 0.12f, 0.3f);
        }

        private void OnBattleEnded()
        {
            var win = _director.State.Phase == BattlePhase.Victory;
            PlayTone(win ? 660f : 150f, 0.15f, win ? 0.5f : 0.6f);
        }

        private void PlayTone(float freq, float volume, float duration)
        {
            if (freq <= 0 || _source == null) return;
            var clip = ProceduralAudio.CreateTone(freq, duration, volume);
            _source.PlayOneShot(clip);
        }
    }

    public static class ProceduralAudio
    {
        public static AudioClip CreateTone(float frequency, float duration, float volume)
        {
            var sampleRate = 44100;
            var samples = Mathf.CeilToInt(sampleRate * duration);
            var data = new float[samples];
            for (var i = 0; i < samples; i++)
            {
                var t = i / (float)sampleRate;
                var env = Mathf.Clamp01(1f - t / duration);
                data[i] = Mathf.Sin(2f * Mathf.PI * frequency * t) * volume * env;
            }
            var clip = AudioClip.Create("tone", samples, 1, sampleRate, false);
            clip.SetData(data, 0);
            return clip;
        }
    }
}
