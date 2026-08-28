using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Procedural battle audio — phases, boss themes, fury ticks, network cues.
    /// </summary>
    [RequireComponent(typeof(AudioSource))]
    public class BattleAudioController : MonoBehaviour
    {
        [SerializeField] [Range(0f, 1f)] private float masterVolume = 0.85f;
        [SerializeField] private bool spatialBossCues = true;

        private AudioSource _source;
        private AudioSource _bossSource;
        private BattleDirector _director;
        private int _lastFuryTurns = -99;
        private float _furyTickCooldown;

        public void Bind(BattleDirector director)
        {
            _director = director;
            _source = GetComponent<AudioSource>();
            _source.playOnAwake = false;
            _source.spatialBlend = 0f;

            _bossSource = gameObject.AddComponent<AudioSource>();
            _bossSource.playOnAwake = false;
            _bossSource.spatialBlend = spatialBossCues ? 1f : 0f;
            _bossSource.minDistance = 0.4f;
            _bossSource.maxDistance = 4f;

            _director.OnPhaseChanged.AddListener(OnPhaseChanged);
            _director.OnLogAdded.AddListener(OnLog);
            _director.OnBattleEnded.AddListener(OnBattleEnded);
            _director.OnCastInterrupted.AddListener(OnCastInterrupted);
            _director.OnBossChanged.AddListener(OnBossChanged);
            BattleNetSession.OnRoleChanged += OnNetRoleChanged;
        }

        private void OnDestroy()
        {
            BattleNetSession.OnRoleChanged -= OnNetRoleChanged;
            if (_director == null) return;
            _director.OnPhaseChanged.RemoveListener(OnPhaseChanged);
            _director.OnLogAdded.RemoveListener(OnLog);
            _director.OnBattleEnded.RemoveListener(OnBattleEnded);
            _director.OnCastInterrupted.RemoveListener(OnCastInterrupted);
            _director.OnBossChanged.RemoveListener(OnBossChanged);
        }

        private void Update()
        {
            if (_director == null) return;
            TickFuryCastAudio(_director.State.Boss.FuryCastTurns);
        }

        private void TickFuryCastAudio(int furyTurns)
        {
            if (furyTurns <= 0)
            {
                _lastFuryTurns = furyTurns;
                return;
            }

            if (furyTurns != _lastFuryTurns)
            {
                _lastFuryTurns = furyTurns;
                var bossId = _director?.Engine.BossId ?? "earth";
                var urgentFreq = bossId switch { "wind" => 880f, "ice" => 784f, "fire" => 932f, _ => 880f };
                var warnFreq = bossId switch { "wind" => 520f, "ice" => 494f, "fire" => 554f, _ => 520f };
                PlayBossCue(furyTurns == 1 ? urgentFreq : warnFreq, 0.1f, 0.22f);
            }

            _furyTickCooldown -= Time.deltaTime;
            if (_furyTickCooldown > 0f) return;

            var interval = furyTurns == 1 ? 0.35f : 0.55f;
            _furyTickCooldown = interval;
            var tickBossId = _director?.Engine.BossId ?? "earth";
            var tickUrgent = tickBossId switch { "wind" => 660f, "ice" => 622f, "fire" => 698f, _ => 660f };
            var tickWarn = tickBossId switch { "wind" => 440f, "ice" => 415f, "fire" => 466f, _ => 440f };
            PlayBossCue(furyTurns == 1 ? tickUrgent : tickWarn, 0.04f, 0.14f);
        }

        private void OnPhaseChanged(BattlePhase phase)
        {
            PlayMain(phase switch
            {
                BattlePhase.Move => 440f,
                BattlePhase.Action => 523f,
                BattlePhase.Weave => 587f,
                BattlePhase.Resolve => 330f,
                BattlePhase.Warning => 280f,
                _ => 0f
            }, 0.08f, 0.15f);
        }

        private void OnLog(string msg)
        {
            if (msg.Contains("伤害")) PlayMain(220f, 0.05f, 0.12f, true);
            else if (msg.Contains("治疗")) PlayMain(880f, 0.06f, 0.18f);
            else if (msg.Contains("打断")) PlayMain(1200f, 0.04f, 0.2f);
            else if (msg.Contains("预警")) PlaySweep(180f, 90f, 0.18f, 0.2f);
            else if (msg.Contains("即死") || msg.Contains("倒下")) PlayMain(110f, 0.12f, 0.3f, true);
        }

        private void OnCastInterrupted()
        {
            PlayMain(1400f, 0.08f, 0.28f);
            PlayChord(new[] { 880f, 1108f, 1318f }, 0.12f, 0.2f);
        }

        private void OnBossChanged(string bossId)
        {
            switch (bossId)
            {
                case "wind":
                    PlayChord(new[] { 392f, 494f, 587f }, 0.2f, 0.22f);
                    break;
                case "ice":
                    PlayChord(new[] { 440f, 554f, 659f }, 0.2f, 0.22f);
                    break;
                case "fire":
                    PlayChord(new[] { 311f, 392f, 466f }, 0.2f, 0.24f);
                    break;
                default:
                    PlayChord(new[] { 262f, 330f, 392f }, 0.2f, 0.22f);
                    break;
            }
        }

        private void OnNetRoleChanged(NetSessionRole role, string transport)
        {
            PlayMain(role switch
            {
                NetSessionRole.Host => 523f,
                NetSessionRole.Client => 659f,
                _ => 392f
            }, 0.06f, 0.18f);
        }

        private void OnBattleEnded()
        {
            var win = _director.State.Phase == BattlePhase.Victory;
            if (win)
                PlayChord(new[] { 523f, 659f, 784f, 1046f }, 0.45f, 0.28f);
            else
                PlaySweep(220f, 80f, 0.55f, 0.25f);
        }

        private void PlayMain(float freq, float volume, float duration, bool noise = false)
        {
            if (freq <= 0 || _source == null) return;
            var clip = noise
                ? ProceduralAudio.CreateNoiseBurst(duration, volume * masterVolume)
                : ProceduralAudio.CreateTone(freq, duration, volume * masterVolume);
            _source.PlayOneShot(clip);
        }

        private void PlayBossCue(float freq, float volume, float duration)
        {
            if (_bossSource == null) return;
            var clip = ProceduralAudio.CreateTone(freq, duration, volume * masterVolume);
            _bossSource.PlayOneShot(clip);
        }

        private void PlayChord(float[] freqs, float duration, float volume)
        {
            if (_source == null) return;
            _source.PlayOneShot(ProceduralAudio.CreateChord(freqs, duration, volume * masterVolume));
        }

        private void PlaySweep(float from, float to, float duration, float volume)
        {
            if (_source == null) return;
            _source.PlayOneShot(ProceduralAudio.CreateSweep(from, to, duration, volume * masterVolume));
        }
    }
}
