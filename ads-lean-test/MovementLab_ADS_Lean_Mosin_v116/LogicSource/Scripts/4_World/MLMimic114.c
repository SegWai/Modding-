// In-memory locomotion/pose recorder. Only the designated female actor receives
// playback overrides; the selected player's input, camera and position are read.
class MLMimic114Frame
{
 float Time;
 vector Offset;
 float Yaw;
 float Speed;
 float MoveAngle;
 float Lean;
 float AimX;
 float AimY;
 int Stance = DayZPlayerConstants.STANCEIDX_ERECT;
 bool Raised;
 bool ADS;
};
class MLMimic114Controller
{
 ref array<ref MLMimic114Frame> Frames = new array<ref MLMimic114Frame>;
 PlayerBase Actor;
 bool Recording;
 bool Playing;
 vector Home;
 vector HomeOrientation;
 protected vector m_RecordOrigin;
 protected float m_RecordYaw;
 protected int m_RecordStart;
 protected float m_SampleElapsed;
 protected float m_PlayTime;
 protected int m_Cursor;
 protected string m_WeaponType;
 protected ref TStringArray m_Parts = new TStringArray;
 static float DeltaAngle(float destination, float origin)
 {
  float difference = destination - origin;
  while (difference > 180)
   difference -= 360;
  while (difference < -180)
   difference += 360;
  return difference;
 }
 static vector ToLocal(vector world, float yaw)
 {
  float radians = yaw * Math.DEG2RAD;
  float c = Math.Cos(radians);
  float s = Math.Sin(radians);
  return Vector(world[0] * c - world[2] * s, world[1], world[0] * s + world[2] * c);
 }
 static vector ToWorld(vector localOffset, float yaw)
 {
  float radians = yaw * Math.DEG2RAD;
  float c = Math.Cos(radians);
  float s = Math.Sin(radians);
  return Vector(localOffset[0] * c + localOffset[2] * s, localOffset[1], -localOffset[0] * s + localOffset[2] * c);
 }
 void AttachActor(PlayerBase actor, vector home, vector orientation)
 {
  StopPlayback();
  Actor = actor;
  Home = home;
  HomeOrientation = orientation;
  if (Actor)
   Actor.ML114EnableMimic();
 }
 void ToggleRecording()
 {
  if (Playing)
  {
   StopPlayback();
   return;
  }
  if (Recording)
  {
   Capture();
   Recording = false;
   Print("[MLMIMIC114] recording_stopped frames=" + Frames.Count());
   return;
  }
  PlayerBase source = PlayerBase.Cast(GetGame().GetPlayer());
  if (!source || !source.IsAlive())
   return;
  Frames.Clear();
  m_RecordOrigin = source.GetPosition();
  vector orientation = source.GetOrientation();
  m_RecordYaw = orientation[0];
  m_RecordStart = GetGame().GetTime();
  m_SampleElapsed = 0;
  m_WeaponType = "";
  m_Parts.Clear();
  EntityAI held = source.GetHumanInventory().GetEntityInHands();
  if (Weapon_Base.Cast(held))
  {
   m_WeaponType = held.GetType();
   for (int i = 0; i < held.GetInventory().AttachmentCount(); i++)
   {
    EntityAI part = held.GetInventory().GetAttachmentFromIndex(i);
    if (part && !Magazine.Cast(part))
     m_Parts.Insert(part.GetType());
   }
  }
  Recording = true;
  Capture();
  Print("[MLMIMIC114] recording_started weapon=" + m_WeaponType);
 }
 void Capture()
 {
  if (!Recording || Frames.Count() >= 6000)
   return;
  PlayerBase source = PlayerBase.Cast(GetGame().GetPlayer());
  if (!source || !source.IsAlive())
  {
   Recording = false;
   return;
  }
  HumanMovementState state = new HumanMovementState();
  source.GetMovementState(state);
  MLMimic114Frame frame = new MLMimic114Frame;
  frame.Time = (GetGame().GetTime() - m_RecordStart) * 0.001;
  if (Frames.Count() > 0 && frame.Time <= Frames[Frames.Count() - 1].Time)
   return;
  frame.Offset = ToLocal(source.GetPosition() - m_RecordOrigin, m_RecordYaw);
  vector orientation = source.GetOrientation();
  frame.Yaw = DeltaAngle(orientation[0], m_RecordYaw);
  frame.Stance = state.m_iStanceIdx;
  frame.Lean = state.m_fLeaning;
  frame.Raised = source.IsRaised();
  frame.ADS = source.IsInIronsights() || source.IsInOptics();
  HumanCommandMove move = source.GetCommand_Move();
  if (move)
  {
   frame.Speed = move.GetCurrentMovementSpeed();
   frame.MoveAngle = move.GetCurrentMovementAngle();
  }
  HumanCommandWeapons weapon = source.GetCommandModifier_Weapons();
  if (weapon)
  {
   frame.AimX = weapon.GetBaseAimingAngleLR();
   frame.AimY = weapon.GetBaseAimingAngleUD();
  }
  Frames.Insert(frame);
  if (Frames.Count() >= 6000)
  {
   Recording = false;
   Print("[MLMIMIC114] recording_stopped frame_limit=6000");
  }
 }
 void StartPlayback()
 {
  if (Recording)
  {
   Capture();
   Recording = false;
  }
  if (!Actor || !Actor.IsAlive() || Frames.Count() < 2)
   return;
  if (Frames[Frames.Count() - 1].Time < 0.05)
   return;
  PrepareWeapon();
  Playing = true;
  m_PlayTime = 0;
  m_Cursor = 0;
  Actor.SetPosition(Home);
  Actor.SetOrientation(HomeOrientation);
  ApplyFrame();
  Print("[MLMIMIC114] loop_started duration=" + Frames[Frames.Count() - 1].Time);
 }
 void PrepareWeapon()
 {
  if (!Actor)
   return;
  EntityAI held = Actor.GetHumanInventory().GetEntityInHands();
  if (held && held.GetType() == m_WeaponType)
   return;
  if (held)
   GetGame().ObjectDelete(held);
  if (m_WeaponType == "")
   return;
  Weapon_Base weapon = Weapon_Base.Cast(Actor.GetHumanInventory().CreateInHands(m_WeaponType));
  if (!weapon || !weapon.CanProcessWeaponEvents())
  {
   Print("[MLMIMIC114] weapon_unavailable=" + m_WeaponType);
   return;
  }
  foreach (string type : m_Parts)
  {
   EntityAI part = weapon.GetInventory().CreateAttachment(type);
   if (part && part.GetCompEM())
    part.GetInventory().CreateAttachment("Battery9V");
  }
  weapon.SpawnAmmo();
 }
 void StopPlayback()
 {
  Playing = false;
  if (Actor)
   Actor.ML114HoldMimic();
 }
 void Reset()
 {
  StopPlayback();
  Recording = false;
  Frames.Clear();
  m_PlayTime = 0;
  m_Cursor = 0;
  if (Actor && Actor.IsAlive())
  {
   Actor.SetPosition(Home);
   Actor.SetOrientation(HomeOrientation);
   Actor.ML114ResetMimicPose();
  }
  Print("[MLMIMIC114] cleared");
 }
 void Tick(float dt)
 {
  if (GetGame().IsMultiplayer())
   return;
  if (Recording)
  {
   m_SampleElapsed += dt;
   if (m_SampleElapsed >= 0.05)
   {
    m_SampleElapsed = 0;
    Capture();
   }
  }
  if (!Playing)
   return;
  if (!Actor || !Actor.IsAlive() || Frames.Count() < 2)
  {
   StopPlayback();
   return;
  }
  float duration = Frames[Frames.Count() - 1].Time;
  m_PlayTime += dt;
  if (m_PlayTime >= duration)
  {
   m_PlayTime = Math.ModFloat(m_PlayTime, duration);
   m_Cursor = 0;
   Actor.SetPosition(Home);
  }
  ApplyFrame();
 }
 void ApplyFrame()
 {
  while (m_Cursor + 1 < Frames.Count() - 1 && Frames[m_Cursor + 1].Time <= m_PlayTime)
   m_Cursor++;
  MLMimic114Frame a = Frames[m_Cursor];
  MLMimic114Frame b = Frames[m_Cursor + 1];
  float span = Math.Max(0.001, b.Time - a.Time);
  float alpha = Math.Clamp((m_PlayTime - a.Time) / span, 0, 1);
  MLMimic114Frame frame = new MLMimic114Frame;
  frame.Offset = a.Offset + (b.Offset - a.Offset) * alpha;
  frame.Yaw = a.Yaw + DeltaAngle(b.Yaw, a.Yaw) * alpha;
  frame.Speed = a.Speed + (b.Speed - a.Speed) * alpha;
  frame.MoveAngle = a.MoveAngle + DeltaAngle(b.MoveAngle, a.MoveAngle) * alpha;
  frame.Lean = a.Lean + (b.Lean - a.Lean) * alpha;
  frame.AimX = a.AimX + DeltaAngle(b.AimX, a.AimX) * alpha;
  frame.AimY = a.AimY + (b.AimY - a.AimY) * alpha;
  frame.Stance = a.Stance;
  frame.Raised = a.Raised;
  frame.ADS = a.ADS;
  vector position = Home + ToWorld(frame.Offset, HomeOrientation[0]);
  float heading = HomeOrientation[0] + frame.Yaw;
  Actor.ML114SetMimicFrame(frame, position, heading);
 }
};
