<template>
  <section
    ref="heroRef"
    class="auth-hero compass-hero"
    @pointermove="handleHeroPointerMove"
    @pointerleave="resetHeroPointer"
  >
    <div class="compass-hero-noise"></div>

    <div class="compass-scene">
      <div class="compass-glow compass-glow-left"></div>
      <div class="compass-glow compass-glow-right"></div>

      <div class="compass-characters">
        <div class="compass-character chicken" :style="characterStyle('chicken')">
          <div class="compass-character-shadow"></div>
          <div class="compass-character-body"></div>
          <div class="compass-character-leg left"></div>
          <div class="compass-character-leg right"></div>
          <div class="compass-character-arm left" :style="armStyle('chicken', 'left')"></div>
          <div class="compass-character-arm right" :style="armStyle('chicken', 'right')"></div>
          <div class="compass-character-head" :style="headStyle('chicken')">
            <div class="compass-cat-ear left"></div>
            <div class="compass-cat-ear right"></div>
            <div class="compass-face compass-cat-face">
              <span class="compass-eye"><i :style="pupilStyle('chicken')"></i></span>
              <span class="compass-eye"><i :style="pupilStyle('chicken')"></i></span>
            </div>
            <div class="compass-cat-nose"></div>
            <div class="compass-mouth smile"></div>
            <div class="compass-cat-whiskers left"></div>
            <div class="compass-cat-whiskers right"></div>
          </div>
        </div>

        <div class="compass-character duck" :style="characterStyle('duck')">
          <div class="compass-character-shadow"></div>
          <div class="compass-character-body"></div>
          <div class="compass-character-leg left"></div>
          <div class="compass-character-leg right"></div>
          <div class="compass-character-arm left" :style="armStyle('duck', 'left')"></div>
          <div class="compass-character-arm right" :style="armStyle('duck', 'right')"></div>
          <div class="compass-character-head" :style="headStyle('duck')">
            <div class="compass-frog-eye-dome left">
              <span class="compass-eye"><i :style="pupilStyle('duck')"></i></span>
            </div>
            <div class="compass-frog-eye-dome right">
              <span class="compass-eye"><i :style="pupilStyle('duck')"></i></span>
            </div>
            <div class="compass-frog-cheek left"></div>
            <div class="compass-frog-cheek right"></div>
            <div class="compass-mouth smile"></div>
          </div>
        </div>

        <div class="compass-character goose" :style="characterStyle('goose')">
          <div class="compass-character-shadow"></div>
          <div class="compass-character-body"></div>
          <div class="compass-character-leg left"></div>
          <div class="compass-character-leg right"></div>
          <div class="compass-character-arm left" :style="armStyle('goose', 'left')"></div>
          <div class="compass-character-arm right" :style="armStyle('goose', 'right')"></div>
          <div class="compass-character-head" :style="headStyle('goose')">
            <div class="compass-fox-ear left"></div>
            <div class="compass-fox-ear right"></div>
            <div class="compass-fox-mask"></div>
            <div class="compass-face compass-fox-face">
              <span class="compass-eye"><i :style="pupilStyle('goose')"></i></span>
              <span class="compass-eye"><i :style="pupilStyle('goose')"></i></span>
            </div>
            <div class="compass-fox-snout"></div>
          </div>
        </div>

        <div class="compass-character dog" :style="characterStyle('dog')">
          <div class="compass-character-shadow"></div>
          <div class="compass-character-body"></div>
          <div class="compass-character-leg left"></div>
          <div class="compass-character-leg right"></div>
          <div class="compass-character-arm left" :style="armStyle('dog', 'left')"></div>
          <div class="compass-character-arm right" :style="armStyle('dog', 'right')"></div>
          <div class="compass-character-head" :style="headStyle('dog')">
            <div class="compass-owl-tuft left"></div>
            <div class="compass-owl-tuft right"></div>
            <div class="compass-owl-eye-ring left">
              <span class="compass-eye"><i :style="pupilStyle('dog')"></i></span>
            </div>
            <div class="compass-owl-eye-ring right">
              <span class="compass-eye"><i :style="pupilStyle('dog')"></i></span>
            </div>
            <div class="compass-owl-beak"></div>
          </div>
        </div>

        <div class="compass-character pig" :style="characterStyle('pig')">
          <div class="compass-character-shadow"></div>
          <div class="compass-character-body"></div>
          <div class="compass-character-leg left"></div>
          <div class="compass-character-leg right"></div>
          <div class="compass-character-arm left" :style="armStyle('pig', 'left')"></div>
          <div class="compass-character-arm right" :style="armStyle('pig', 'right')"></div>
          <div class="compass-character-head" :style="headStyle('pig')">
            <div class="compass-ear left"></div>
            <div class="compass-ear right"></div>
            <div class="compass-pig-blush left"></div>
            <div class="compass-pig-blush right"></div>
            <div class="compass-face">
              <span class="compass-eye"><i :style="pupilStyle('pig')"></i></span>
              <span class="compass-eye"><i :style="pupilStyle('pig')"></i></span>
            </div>
            <div class="compass-snout"></div>
            <div class="compass-mouth"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'

const heroRef = ref(null)

const pointer = reactive({
  x: 0,
  y: 0,
})

const characterFactors = {
  chicken: { x: -0.44, y: -0.24, rotate: -4.2, tilt: -10, lift: 0, scale: 0.84 },
  duck: { x: -0.22, y: 0.28, rotate: -2.4, tilt: -6, lift: 0, scale: 1.12 },
  goose: { x: 0.1, y: 0.1, rotate: 1.6, tilt: 2, lift: 0, scale: 1.62 },
  dog: { x: 0.34, y: -0.22, rotate: 3.8, tilt: 12, lift: 0, scale: 1.3 },
  pig: { x: 0.32, y: 0.2, rotate: 3.2, tilt: 7, lift: 0, scale: 1.92 },
}

function handleHeroPointerMove(event) {
  const hero = heroRef.value
  if (!hero) {
    return
  }
  const rect = hero.getBoundingClientRect()
  const normalizedX = ((event.clientX - rect.left) / rect.width) * 2 - 1
  const normalizedY = ((event.clientY - rect.top) / rect.height) * 2 - 1
  pointer.x = Math.max(-1, Math.min(1, normalizedX))
  pointer.y = Math.max(-1, Math.min(1, normalizedY))
}

function resetHeroPointer() {
  pointer.x = 0
  pointer.y = 0
}

function pupilStyle(name) {
  const factor = characterFactors[name]
  return {
    transform: `translate(${pointer.x * 10 * factor.x}px, ${pointer.y * 8 * factor.y}px)`,
  }
}

function headStyle(name) {
  const factor = characterFactors[name]
  return {
    transform: `translate(${pointer.x * 14 * factor.x}px, ${pointer.y * 10 * factor.y}px) rotate(${pointer.x * factor.rotate}deg)`,
  }
}

function characterStyle(name) {
  const factor = characterFactors[name]
  return {
    transform: `translate(${pointer.x * 16 * factor.x}px, ${pointer.y * 14 * factor.y}px) rotate(${factor.tilt + pointer.x * factor.rotate * 0.6}deg) scale(${factor.scale})`,
  }
}

function armStyle(name, side) {
  const sign = side === 'left' ? -1 : 1
  return {
    transform: `translate(${pointer.x * 7 * sign}px, ${pointer.y * 5}px) rotate(${16 * sign + pointer.x * 8 * sign}deg)`,
  }
}
</script>
