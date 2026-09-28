import collections
import math
import random
import time
import cv2
import mediapipe as mp
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
WIDTH, HEIGHT = 900, 750
NUM_PARTICLES = 1400

# Color definitions
COLOR_BG = (10, 12, 22)
COLOR_TEXT = (230, 240, 255)
COLOR_ACCENT = (100, 180, 255)

# Initialize Pygame
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Gesture Cosmic Particle Engine")
clock = pygame.time.Clock()
font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 22, bold=True)
font_sub = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15)
font_badge = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

# ==============================================================================
# 3D SHAPE GENERATORS
# ==============================================================================

def generate_heart_points(num):
  """1 FINGER: 3D Pulsing Anatomical/Romantic Heart Curve."""
  pts = []
  for _ in range(num):
    t = random.uniform(0, 2 * math.pi)
    hx = 16 * (math.sin(t) ** 3)
    hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    # Depth distribution: thicker towards center, tapering at edges
    envelope = max(0.1, 1.0 - (abs(hx) / 18.0) * 0.7)
    hz = random.uniform(-4.5, 4.5) * envelope

    # Color grading: Inner hot magenta/gold to outer ruby red
    dist_center = math.hypot(hx, hy)
    if dist_center < 7:
      color = (255, random.randint(180, 220), random.randint(200, 240))
    elif dist_center < 13:
      color = (255, random.randint(40, 90), random.randint(140, 200))
    else:
      color = (random.randint(220, 255), random.randint(20, 50), random.randint(60, 100))

    pts.append({
        "tx": hx * 12.0,
        "ty": hy * 12.0,
        "tz": hz * 12.0,
        "color": color,
        "size": random.uniform(2.0, 4.2),
        "blink_speed": random.uniform(2.5, 5.0),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })
  return pts


def generate_ily_points(num):
  """2 FINGERS: 3D 'I ❤ U' Hologram."""
  pts = []
  num_i = int(num * 0.22)
  num_heart = int(num * 0.52)
  num_u = num - num_i - num_heart

  # --- LETTER 'I' ---
  for _ in range(num_i):
    sub = random.random()
    if sub < 0.6:  # Vertical backbone
      x = -180 + random.uniform(-7, 7)
      y = random.uniform(-90, 90)
    elif sub < 0.8:  # Top crossbar
      x = -180 + random.uniform(-35, 35)
      y = -90 + random.uniform(-7, 7)
    else:  # Bottom crossbar
      x = -180 + random.uniform(-35, 35)
      y = 90 + random.uniform(-7, 7)
    z = random.uniform(-14, 14)
    color = (random.randint(120, 180), random.randint(210, 255), 255)
    pts.append({
        "tx": x, "ty": y, "tz": z, "color": color,
        "size": random.uniform(2.2, 3.8),
        "blink_speed": random.uniform(1.8, 3.5),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  # --- CENTRAL 3D HEART '❤' ---
  for _ in range(num_heart):
    t = random.uniform(0, 2 * math.pi)
    hx = 16 * (math.sin(t) ** 3)
    hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    hz = random.uniform(-3.5, 3.5)
    color = (255, random.randint(30, 90), random.randint(130, 210))
    pts.append({
        "tx": hx * 6.5,
        "ty": hy * 6.5,
        "tz": hz * 6.5,
        "color": color,
        "size": random.uniform(2.2, 4.0),
        "blink_speed": random.uniform(3.0, 6.0),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  # --- LETTER 'U' ---
  for _ in range(num_u):
    sub = random.random()
    if sub < 0.35:  # Left leg
      x = 145 + random.uniform(-7, 7)
      y = random.uniform(-90, 30)
    elif sub < 0.70:  # Right leg
      x = 215 + random.uniform(-7, 7)
      y = random.uniform(-90, 30)
    else:  # Bottom semicircle curve
      phi = random.uniform(0, math.pi)
      r = 35 + random.uniform(-6, 6)
      x = 180 - r * math.cos(phi)
      y = 30 + r * math.sin(phi)
    z = random.uniform(-14, 14)
    color = (random.randint(210, 255), random.randint(130, 180), 255)
    pts.append({
        "tx": x, "ty": y, "tz": z, "color": color,
        "size": random.uniform(2.2, 3.8),
        "blink_speed": random.uniform(1.8, 3.5),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  return pts


def generate_globe_points(num):
  """3 FINGERS: 3D Celestial Rotating Space Globe with Orbital Ring."""
  pts = []
  num_sphere = int(num * 0.72)
  num_ring = num - num_sphere
  R = 135.0

  # Spherical Globe with Latitude & Longitude grid bands
  for _ in range(num_sphere):
    theta = random.uniform(0, 2 * math.pi)
    cost = random.uniform(-1.0, 1.0)
    phi = math.acos(cost)

    sx = R * math.sin(phi) * math.cos(theta)
    sy = R * math.cos(phi)
    sz = R * math.sin(phi) * math.sin(theta)

    # Color layers: Continents, Oceans, Atmospheric Aurora
    lat = abs(sy) / R
    if lat > 0.82:  # Polar ice caps
      color = (230, 245, 255)
    elif lat < 0.25:  # Tropical emerald / cyan
      color = (random.randint(30, 70), random.randint(210, 255), random.randint(170, 220))
    else:  # Deep space ocean blue
      color = (random.randint(20, 60), random.randint(140, 200), random.randint(230, 255))

    pts.append({
        "tx": sx, "ty": sy, "tz": sz, "color": color,
        "size": random.uniform(1.8, 3.4),
        "blink_speed": random.uniform(1.2, 2.5),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  # Tilted Planetary Ring (Saturn-like)
  tilt_angle = math.radians(24)
  cos_tilt = math.cos(tilt_angle)
  sin_tilt = math.sin(tilt_angle)

  for _ in range(num_ring):
    ring_r = random.uniform(165.0, 230.0)
    ring_theta = random.uniform(0, 2 * math.pi)
    rx = ring_r * math.cos(ring_theta)
    rz = ring_r * math.sin(ring_theta)
    ry = random.uniform(-3, 3)

    # Apply tilt rotation around X-axis
    ry_tilted = ry * cos_tilt - rz * sin_tilt
    rz_tilted = ry * sin_tilt + rz * cos_tilt

    color = (random.randint(230, 255), random.randint(190, 230), random.randint(90, 150))
    pts.append({
        "tx": rx, "ty": ry_tilted, "tz": rz_tilted, "color": color,
        "size": random.uniform(1.6, 3.0),
        "blink_speed": random.uniform(2.0, 4.0),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  return pts


def generate_galaxy_points(num):
  """5 FINGERS / OPEN PALM: Majestic 4-Arm Spiral Galaxy with Blinking Stars."""
  pts = []
  num_core = int(num * 0.20)
  num_arms = num - num_core
  arms_count = 4

  # Radiant Galactic Core
  for _ in range(num_core):
    r = random.triangular(0, 48, 12)
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0, math.pi)
    cx = r * math.sin(phi) * math.cos(theta)
    cy = r * math.cos(phi) * 0.6  # Compressed vertically
    cz = r * math.sin(phi) * math.sin(theta)

    color = (255, random.randint(220, 255), random.randint(160, 210))
    pts.append({
        "tx": cx, "ty": cy, "tz": cz, "color": color,
        "size": random.uniform(2.5, 4.5),
        "blink_speed": random.uniform(2.0, 4.5),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  # Spiral Galaxy Arms
  for i in range(num_arms):
    arm_idx = i % arms_count
    arm_offset = arm_idx * (2 * math.pi / arms_count)
    dist = random.triangular(35, 260, 95)
    # Logarithmic winding curve
    spiral_theta = (dist / 26.0) + arm_offset + random.gauss(0, 0.22)

    gx = dist * math.cos(spiral_theta)
    gz = dist * math.sin(spiral_theta)
    # Disk thickness diminishes toward periphery
    thickness = max(5.0, 24.0 * (1.0 - dist / 280.0))
    gy = random.gauss(0, thickness * 0.5)

    # Cosmic Palette: Deep Purple, Stellar Cyan, Magenta & Diamond White
    dice = random.random()
    if dice < 0.35:
      color = (random.randint(150, 200), random.randint(60, 110), 255)
    elif dice < 0.70:
      color = (random.randint(40, 90), random.randint(210, 255), 255)
    elif dice < 0.90:
      color = (255, random.randint(70, 130), random.randint(180, 240))
    else:
      color = (245, 250, 255)

    pts.append({
        "tx": gx, "ty": gy, "tz": gz, "color": color,
        "size": random.uniform(1.8, 3.8),
        "blink_speed": random.uniform(2.5, 6.0),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })

  return pts


def generate_capture_points(num):
  """CLOSED PALM / FIST: Galaxy Singularity Capture Vortex (Black Hole)."""
  pts = []
  for _ in range(num):
    # Stars sucked inward into a high-energy compressed vortex disk
    dist = random.triangular(6.0, 52.0, 16.0)
    theta = random.uniform(0, 2 * math.pi)

    vx = dist * math.cos(theta)
    vz = dist * math.sin(theta)
    vy = random.gauss(0, 4.0) * (dist / 52.0)

    # Ultra-hot plasma colors: Electric Cyan, Blazing Violet, White-hot Singularity
    if dist < 14:
      color = (255, 255, 255)  # Event horizon brilliant core
    elif dist < 30:
      color = (random.randint(0, 80), random.randint(220, 255), 255)
    else:
      color = (random.randint(210, 255), random.randint(30, 80), random.randint(210, 255))

    pts.append({
        "tx": vx, "ty": vy, "tz": vz, "color": color,
        "size": random.uniform(1.8, 3.6),
        "blink_speed": random.uniform(4.0, 8.0),
        "blink_phase": random.uniform(0, 2 * math.pi),
    })
  return pts


# ==============================================================================
# PARTICLE SYSTEM STATE & INTERPOLATION ENGINE
# ==============================================================================
class ParticleSystem:
  def __init__(self, count):
    self.count = count
    # Initialize initial shape (Galaxy)
    initial_shape = generate_galaxy_points(count)

    # Particle dynamic arrays for maximum performance
    self.x = np.array([p["tx"] for p in initial_shape], dtype=np.float32)
    self.y = np.array([p["ty"] for p in initial_shape], dtype=np.float32)
    self.z = np.array([p["tz"] for p in initial_shape], dtype=np.float32)

    self.tx = self.x.copy()
    self.ty = self.y.copy()
    self.tz = self.z.copy()

    self.vx = np.zeros(count, dtype=np.float32)
    self.vy = np.zeros(count, dtype=np.float32)
    self.vz = np.zeros(count, dtype=np.float32)

    self.r = np.array([p["color"][0] for p in initial_shape], dtype=np.float32)
    self.g = np.array([p["color"][1] for p in initial_shape], dtype=np.float32)
    self.b = np.array([p["color"][2] for p in initial_shape], dtype=np.float32)

    self.tr = self.r.copy()
    self.tg = self.g.copy()
    self.tb = self.b.copy()

    self.sizes = np.array([p["size"] for p in initial_shape], dtype=np.float32)
    self.target_sizes = self.sizes.copy()

    self.blink_speed = np.array([p["blink_speed"] for p in initial_shape], dtype=np.float32)
    self.blink_phase = np.array([p["blink_phase"] for p in initial_shape], dtype=np.float32)

    self.current_shape_id = "GALAXY"
    self.base_targets = initial_shape

  def morph_to(self, shape_id, new_points):
    if self.current_shape_id == shape_id:
      return
    self.current_shape_id = shape_id
    self.base_targets = new_points

    # Set new targets
    for i, p in enumerate(new_points):
      self.tx[i] = p["tx"]
      self.ty[i] = p["ty"]
      self.tz[i] = p["tz"]
      self.tr[i] = p["color"][0]
      self.tg[i] = p["color"][1]
      self.tb[i] = p["color"][2]
      self.target_sizes[i] = p["size"]
      self.blink_speed[i] = p["blink_speed"]
      self.blink_phase[i] = p["blink_phase"]

  def update(self, dt, current_time, is_capture=False):
    # Dynamic pulse animation for heart
    if self.current_shape_id in ("HEART", "ILY"):
      # Real anatomical Lub-Dub rhythmic double pulse
      pulse = 1.0 + 0.09 * math.sin(current_time * 6.5) + 0.04 * math.sin(current_time * 13.0)
      mod_tx = self.tx * pulse
      mod_ty = self.ty * pulse
      mod_tz = self.tz * pulse
    elif is_capture:
      # Tight rotational inward vortex acceleration
      vortex_spin = current_time * 4.0
      cos_v = math.cos(vortex_spin * 0.08)
      sin_v = math.sin(vortex_spin * 0.08)
      mod_tx = self.tx * cos_v - self.tz * sin_v
      mod_tz = self.tz * cos_v + self.tx * sin_v
      mod_ty = self.ty
    else:
      mod_tx = self.tx
      mod_ty = self.ty
      mod_tz = self.tz

    # Fluid Spring-Damping Morph Physics (Smooth Lerp + Inertia)
    spring_k = 0.075 if not is_capture else 0.12
    damping = 0.78

    dx = mod_tx - self.x
    dy = mod_ty - self.y
    dz = mod_tz - self.z

    self.vx = self.vx * damping + dx * spring_k
    self.vy = self.vy * damping + dy * spring_k
    self.vz = self.vz * damping + dz * spring_k

    self.x += self.vx
    self.y += self.vy
    self.z += self.vz

    # Smooth color transitions
    color_speed = 0.08
    self.r += (self.tr - self.r) * color_speed
    self.g += (self.tg - self.g) * color_speed
    self.b += (self.tb - self.b) * color_speed
    self.sizes += (self.target_sizes - self.sizes) * 0.08


# Instantiate global particle system
particles = ParticleSystem(NUM_PARTICLES)

# Pre-generate target shape templates
SHAPE_TEMPLATES = {
    "HEART": generate_heart_points(NUM_PARTICLES),
    "ILY": generate_ily_points(NUM_PARTICLES),
    "GLOBE": generate_globe_points(NUM_PARTICLES),
    "GALAXY": generate_galaxy_points(NUM_PARTICLES),
    "CAPTURE": generate_capture_points(NUM_PARTICLES),
}


# ==============================================================================
# GESTURE DETECTION (ROBUST WITH TEMPORAL SMOOTHING)
# ==============================================================================
gesture_history = collections.deque(maxlen=7)


def detect_gesture_instant(landmarks):
  """
  Extract finger states using MediaPipe landmarks:
  Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
  """
  # Fingers 4 (Index to Pinky) extension check
  tips = [8, 12, 16, 20]
  pips = [6, 10, 14, 18]
  mcps = [5, 9, 13, 17]

  fingers = []

  # Thumb logic: check distance to pinky MCP to determine if open/closed
  thumb_tip = landmarks[4]
  thumb_ip = landmarks[3]
  pinky_mcp = landmarks[17]
  thumb_extended = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y) > \
                   math.hypot(thumb_ip.x - pinky_mcp.x, thumb_ip.y - pinky_mcp.y) * 1.15
  fingers.append(1 if thumb_extended else 0)

  # Other 4 fingers
  for tip, pip in zip(tips, pips):
    if landmarks[tip].y < landmarks[pip].y:
      fingers.append(1)
    else:
      fingers.append(0)

  # fingers format: [Thumb, Index, Middle, Ring, Pinky]
  total_extended = sum(fingers)
  index_up = fingers[1] == 1
  middle_up = fingers[2] == 1
  ring_up = fingers[3] == 1
  pinky_up = fingers[4] == 1

  # 1. Closed Palm / Fist (Capture Singularity)
  if total_extended == 0 or (total_extended == 1 and fingers[0] == 1 and not index_up):
    return "CAPTURE"

  # 2. One Finger (Index only) -> 3D Beating Heart
  if index_up and not middle_up and not ring_up and not pinky_up:
    return "HEART"

  # 3. Two Fingers (Index + Middle or Peace or ILY sign) -> 3D I LOVE YOU
  if index_up and middle_up and not ring_up and not pinky_up:
    return "ILY"
  # Also detect ILY sign (Thumb + Index + Pinky)
  if index_up and pinky_up and not middle_up and not ring_up:
    return "ILY"

  # 4. Three Fingers (Index + Middle + Ring or Thumb + Index + Middle) -> 3D Space Globe
  if (index_up and middle_up and ring_up and not pinky_up) or (total_extended == 3 and not pinky_up):
    return "GLOBE"

  # 5. Open Palm (4 or 5 fingers extended) -> 3D Spiral Galaxy
  if total_extended >= 4:
    return "GALAXY"

  return "UNKNOWN"


def get_smoothed_gesture(raw_gesture):
  gesture_history.append(raw_gesture)
  # Filter out UNKNOWN unless all are UNKNOWN
  valid_gestures = [g for g in gesture_history if g != "UNKNOWN"]
  if not valid_gestures:
    return "UNKNOWN"
  # Return mode (most frequent gesture)
  counts = collections.Counter(valid_gestures)
  most_common, freq = counts.most_common(1)[0]
  if freq >= 4:
    return most_common
  return None


# ==============================================================================
# MAIN ENGINE LOOP
# ==============================================================================
current_shape_name = "Spiral Galaxy"
current_shape_badge = "🖐 5 FINGERS: OPEN PALM"
angle_x = 0.15
angle_y = 0.0
scale_factor = 1.0
target_scale = 1.0
last_time = time.time()
running = True

# Shape metadata mapping
SHAPE_INFO = {
    "GALAXY": ("Spiral Galaxy", "🖐 5 FINGERS: OPEN PALM", (100, 200, 255)),
    "CAPTURE": ("Galaxy Singularity (Vortex)", "✊ FIST: CLOSED PALM", (255, 100, 100)),
    "HEART": ("3D Beating Heart", "☝ 1 FINGER: INDEX UP", (255, 80, 150)),
    "ILY": ("3D 'I ❤ U' Hologram", "✌ 2 FINGERS: PEACE / LOVE", (230, 130, 255)),
    "GLOBE": ("Space Globe & Rings", "🤟 3 FINGERS: GLOBE ORBIT", (80, 240, 180)),
}

print("Particle Engine Initialized. Ready for gesture input.")

while running:
  now = time.time()
  dt = min(now - last_time, 0.05)
  last_time = now

  # Event handling
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
        running = False
      # Keyboard shortcuts fallback
      elif event.key == pygame.K_1:
        particles.morph_to("HEART", SHAPE_TEMPLATES["HEART"])
      elif event.key == pygame.K_2:
        particles.morph_to("ILY", SHAPE_TEMPLATES["ILY"])
      elif event.key == pygame.K_3:
        particles.morph_to("GLOBE", SHAPE_TEMPLATES["GLOBE"])
      elif event.key == pygame.K_4 or event.key == pygame.K_5:
        particles.morph_to("GALAXY", SHAPE_TEMPLATES["GALAXY"])
      elif event.key == pygame.K_0 or event.key == pygame.K_c:
        particles.morph_to("CAPTURE", SHAPE_TEMPLATES["CAPTURE"])

  # --- CAMERA & GESTURE PROCESSING ---
  success, frame = cap.read()
  hand_detected = False

  if success:
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
      hand_detected = True
      hand_landmarks = results.multi_hand_landmarks[0]
      mp_drawing.draw_landmarks(
          frame,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style(),
      )

      # Gesture Recognition
      raw_gesture = detect_gesture_instant(hand_landmarks.landmark)
      stable_gesture = get_smoothed_gesture(raw_gesture)

      if stable_gesture and stable_gesture in SHAPE_TEMPLATES:
        particles.morph_to(stable_gesture, SHAPE_TEMPLATES[stable_gesture])
        name, badge, _ = SHAPE_INFO[stable_gesture]
        current_shape_name = name
        current_shape_badge = badge

      # Dynamic Pinch Zoom using Thumb (4) and Index (8)
      thumb_pt = hand_landmarks.landmark[4]
      index_pt = hand_landmarks.landmark[8]
      pinch_dist = math.hypot(thumb_pt.x - index_pt.x, thumb_pt.y - index_pt.y)
      # Interpolate pinch to scale factor (0.55x to 2.2x)
      target_scale = float(np.interp(pinch_dist, [0.03, 0.28], [0.65, 2.0]))

      # Interactive 3D Rotation controlled by hand position
      wrist = hand_landmarks.landmark[0]
      angle_y += (wrist.x - 0.5) * 0.08
      angle_x += (wrist.y - 0.5) * 0.04

    # Show minimal webcam preview
    cv2.putText(
        frame,
        f"Active: {current_shape_name}",
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 200),
        2,
        cv2.LINE_AA,
    )
    cv2.imshow("Gesture Controller Feed (Press Q to exit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
      running = False

  # Scale factor smoothing
  scale_factor += (target_scale - scale_factor) * 0.1

  # Smooth continuous auto-rotation
  if particles.current_shape_id == "CAPTURE":
    angle_y += 0.035  # Fast capture vortex spin
  elif particles.current_shape_id == "GALAXY":
    angle_y += 0.012  # Graceful celestial orbit
  elif particles.current_shape_id == "GLOBE":
    angle_y += 0.016  # Planetary day-night spin
  else:
    angle_y += 0.010

  # Update Particle Physics
  is_capture_active = (particles.current_shape_id == "CAPTURE")
  particles.update(dt, now, is_capture=is_capture_active)

  # ==============================================================================
  # 3D PROJECTION & RENDERING
  # ==============================================================================
  screen.fill(COLOR_BG)

  # Precompute 3D Rotation Matrices
  cos_y = math.cos(angle_y)
  sin_y = math.sin(angle_y)
  cos_x = math.cos(angle_x)
  sin_x = math.sin(angle_x)

  # Vectorized 3D Transformation
  px = particles.x * scale_factor
  py = particles.y * scale_factor
  pz = particles.z * scale_factor

  # Rotate around Y axis
  x1 = px * cos_y - pz * sin_y
  z1 = pz * cos_y + px * sin_y

  # Rotate around X axis
  y2 = py * cos_x - z1 * sin_x
  z2 = z1 * cos_x + py * sin_x
  x2 = x1

  # Perspective Projection
  fov = 500.0
  camera_dist = 420.0
  depth = camera_dist + z2

  # Mask particles that are behind the camera
  valid_mask = depth > 20.0
  persp = fov / np.maximum(depth, 20.0)

  screen_x = (WIDTH / 2.0 + x2 * persp).astype(np.int32)
  screen_y = (HEIGHT / 2.0 + y2 * persp).astype(np.int32)

  # Twinkling & Blinking Stars Shimmer Calculation
  # Sinusoidal brightness variation per star: range 0.45 to 1.15
  shimmer = 0.75 + 0.35 * np.sin(now * particles.blink_speed + particles.blink_phase)
  shimmer = np.clip(shimmer, 0.3, 1.2)

  # Depth shading: closer particles are brighter and slightly larger
  depth_shades = np.clip((z2 + 250.0) / 450.0, 0.35, 1.0)
  final_intensities = depth_shades * shimmer

  # Depth sorting for clean layering
  indices = np.argsort(z2)

  half_w, half_h = WIDTH, HEIGHT

  # Render particles with dual-pass soft glow
  for idx in indices:
    if not valid_mask[idx]:
      continue
    sx = screen_x[idx]
    sy = screen_y[idx]

    if 0 <= sx < half_w and 0 <= sy < half_h:
      intensity = final_intensities[idx]
      base_size = particles.sizes[idx]
      render_radius = max(1, int(base_size * persp[idx] * 0.9))

      # Calculate color with twinkle
      cr = min(255, int(particles.r[idx] * intensity))
      cg = min(255, int(particles.g[idx] * intensity))
      cb = min(255, int(particles.b[idx] * intensity))

      # Outer soft glow halo for brighter/larger stars
      if render_radius >= 3 and intensity > 0.65:
        halo_color = (cr // 3, cg // 3, cb // 3)
        pygame.draw.circle(screen, halo_color, (sx, sy), render_radius + 2)

      # Core brilliant particle
      pygame.draw.circle(screen, (cr, cg, cb), (sx, sy), render_radius)

  # ==============================================================================
  # MODERN GLASSMORPHIC HUD OVERLAY
  # ==============================================================================
  # Top Header Card
  header_rect = pygame.Rect(20, 20, WIDTH - 40, 68)
  header_surf = pygame.Surface((header_rect.width, header_rect.height), pygame.SRCALPHA)
  header_surf.fill((16, 20, 36, 215))
  pygame.draw.rect(header_surf, (50, 70, 110, 150), header_surf.get_rect(), width=1, border_radius=12)
  screen.blit(header_surf, header_rect.topleft)

  # Title & Active Gesture Status
  color_active = SHAPE_INFO.get(particles.current_shape_id, ("-", "-", COLOR_ACCENT))[2]
  title_surface = font_title.render(current_shape_name, True, color_active)
  badge_surface = font_badge.render(f"ACTIVE: {current_shape_badge}", True, (240, 245, 255))
  screen.blit(title_surface, (40, 28))
  screen.blit(badge_surface, (40, 56))

  # Stats on the right
  fps_val = int(clock.get_fps())
  stats_txt = f"{NUM_PARTICLES} Stars | Zoom: {int(scale_factor * 100)}% | FPS: {fps_val}"
  stats_surface = font_sub.render(stats_txt, True, (160, 185, 220))
  screen.blit(stats_surface, (WIDTH - stats_surface.get_width() - 40, 42))

  # Bottom Gesture Guide Bar
  guide_rect = pygame.Rect(20, HEIGHT - 55, WIDTH - 40, 40)
  guide_surf = pygame.Surface((guide_rect.width, guide_rect.height), pygame.SRCALPHA)
  guide_surf.fill((14, 18, 30, 205))
  pygame.draw.rect(guide_surf, (40, 55, 85, 120), guide_surf.get_rect(), width=1, border_radius=10)
  screen.blit(guide_surf, guide_rect.topleft)

  guide_text = (
      "✊ Fist: Capture Singularity  |  ☝ 1: 3D Heart  |  "
      "✌ 2: I ❤ U  |  🤟 3: Space Globe  |  🖐 5: Spiral Galaxy  |  Pinch: Zoom"
  )
  guide_surface = font_sub.render(guide_text, True, (175, 195, 225))
  screen.blit(guide_surface, (guide_rect.centerx - guide_surface.get_width() // 2, HEIGHT - 44))

  pygame.display.flip()
  clock.tick(60)

# ==============================================================================
# CLEANUP
# ==============================================================================
cap.release()
cv2.destroyAllWindows()
pygame.quit()