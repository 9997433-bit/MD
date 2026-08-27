using System;
using System.Reflection;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Wires XRGrabInteractable to PieceToken — grab in Move phase, snap to grid on release.
    /// Uses reflection so Core tests stay free of XRI assembly references.
    /// </summary>
    [RequireComponent(typeof(PieceToken))]
    public class PieceXRGrabController : MonoBehaviour
    {
        private PieceToken _token;
        private BattleDirector _director;
        private BattleTableView _table;
        private CoopController _coop;
        private GridSnapHighlighter _highlighter;

        private object _grabInteractable;
        private Type _grabType;
        private bool _configured;
        private bool _grabbing;
        private GridPos _grabStartPos;
        private float _pieceYOffset;

        public bool IsGrabbing => _grabbing;

        public void Setup(
            PieceToken token,
            BattleDirector director,
            BattleTableView table,
            CoopController coop,
            GridSnapHighlighter highlighter)
        {
            _token = token;
            _director = director;
            _table = table;
            _coop = coop;
            _highlighter = highlighter;
            _pieceYOffset = table != null ? table.CellSize * 0.28f : 0.03f;
            TryConfigureGrab();
        }

        private void Start()
        {
            if (!_configured) TryConfigureGrab();
        }

        private void TryConfigureGrab()
        {
            if (_configured) return;
            _grabType = Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.Interactables.XRGrabInteractable, Unity.XR.Interaction.Toolkit");
            if (_grabType == null) return;

            if (!XRRigFactory.XrActive) return;

            var rb = GetComponent<Rigidbody>();
            if (rb == null) rb = gameObject.AddComponent<Rigidbody>();
            rb.isKinematic = true;
            rb.useGravity = false;
            rb.interpolation = RigidbodyInterpolation.Interpolate;

            _grabInteractable = GetComponent(_grabType);
            if (_grabInteractable == null)
                _grabInteractable = gameObject.AddComponent(_grabType);

            SetEnumProperty("movementType", "Instantaneous");
            SetBoolProperty("throwOnDetach", false);
            SetBoolProperty("trackRotation", false);
            SetBoolProperty("trackPosition", true);

            _configured = true;
        }

        private void SetBoolProperty(string name, bool value)
        {
            var prop = _grabType.GetProperty(name);
            prop?.SetValue(_grabInteractable, value);
        }

        private void SetEnumProperty(string name, string enumLabel)
        {
            var prop = _grabType.GetProperty(name);
            if (prop == null) return;
            var enumType = prop.PropertyType;
            try
            {
                var enumValue = Enum.Parse(enumType, enumLabel);
                prop.SetValue(_grabInteractable, enumValue);
            }
            catch
            {
                // ignore unknown enum layout across XRI versions
            }
        }

        private void Update()
        {
            if (!_configured && XRRigFactory.XrActive)
                TryConfigureGrab();
            if (!_configured || _grabInteractable == null || _director == null) return;

            var isSelected = GetIsSelected();
            if (isSelected && !_grabbing)
                BeginGrab();
            else if (!isSelected && _grabbing)
                EndGrab();
            else if (_grabbing)
                UpdateGrabHover();
        }

        private bool GetIsSelected()
        {
            var prop = _grabType.GetProperty("isSelected", BindingFlags.Instance | BindingFlags.Public);
            if (prop == null) return false;
            return prop.GetValue(_grabInteractable) is true;
        }

        private void BeginGrab()
        {
            if (_director.State.Phase != BattlePhase.Move)
            {
                ForceDeselect();
                return;
            }

            if (_coop != null && !_coop.CanControlUnit(_token.UnitId))
            {
                Debug.Log($"[XR Grab] {_coop.ActivePlayerLabel} 无权控制此棋子");
                ForceDeselect();
                return;
            }

            var unit = _director.State.Party.Find(u => u.Id == _token.UnitId);
            if (unit == null || !unit.Alive)
            {
                ForceDeselect();
                return;
            }

            _grabbing = true;
            _grabStartPos = unit.Pos;
            _token.SetSelected(true);
            _token.SetGrabbing(true);
            _highlighter?.Begin(_table, _pieceYOffset);
        }

        private void UpdateGrabHover()
        {
            if (_table == null) return;
            var hover = _table.WorldToGrid(transform.position);
            _highlighter?.SetHover(hover);
            SnapHeight();
        }

        private void EndGrab()
        {
            _grabbing = false;
            _token.SetGrabbing(false);
            _highlighter?.End();

            if (_director == null || _table == null)
            {
                _token.SetSelected(false);
                return;
            }

            if (_director.State.Phase != BattlePhase.Move)
            {
                _token.SnapToGrid(_grabStartPos);
                _token.SetSelected(false);
                return;
            }

            var dest = _table.WorldToGrid(transform.position);
            if (_director.TryMove(_token.UnitId, dest))
                _token.SnapToGrid(dest);
            else
                _token.SnapToGrid(_grabStartPos);

            _token.SetSelected(false);
        }

        private void SnapHeight()
        {
            if (_table == null) return;
            var hover = _table.WorldToGrid(transform.position);
            var world = _table.GridToWorld(hover.X, hover.Y);
            var p = transform.position;
            transform.position = new Vector3(p.x, world.y + _pieceYOffset, p.z);
        }

        private void ForceDeselect()
        {
            if (_grabInteractable is Behaviour behaviour)
            {
                behaviour.enabled = false;
                behaviour.enabled = true;
            }
        }
    }
}
