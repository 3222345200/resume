<template>
  <div v-if="open" class="avatar-crop-mask" @click.self="handleCancel">
    <section class="avatar-crop-dialog" role="dialog" aria-modal="true" aria-label="图片裁切">
      <header class="avatar-crop-header">
        <h3>图片裁切</h3>
        <button type="button" class="avatar-crop-close" aria-label="关闭裁切窗口" @click="handleCancel">×</button>
      </header>

      <div class="avatar-crop-content">
        <div
          class="avatar-crop-stage-wrap"
          @wheel.prevent="handleWheel"
          @pointerdown="startDrag"
          @pointermove="handleDrag"
          @pointerup="stopDrag"
          @pointercancel="stopDrag"
          @pointerleave="stopDrag"
        >
          <div class="avatar-crop-stage">
            <div class="avatar-crop-image-layer" :style="imageLayerStyle">
              <img v-if="imageUrl" :src="imageUrl" alt="头像裁切预览" draggable="false" />
            </div>
            <div class="avatar-crop-frame">
              <span class="avatar-crop-size-label">{{ cropOutputWidth }} × {{ cropOutputHeight }}</span>
              <i></i><i></i><i></i><i></i>
              <i></i><i></i><i></i><i></i>
            </div>
          </div>
        </div>

        <div class="avatar-crop-side">
          <p class="avatar-crop-tip-title">功能提示：</p>
          <p class="avatar-crop-tip-text">1、鼠标滚轮可以缩放照片</p>
          <p class="avatar-crop-tip-text">2、按住照片拖动可以调整位置</p>

          <div class="avatar-crop-upload-info">
            <p class="avatar-crop-tip-text">点击照片可重新裁切上传，下载 PDF 时会使用同样的裁切结果和固定尺寸。</p>
            <p class="avatar-crop-tip-text">未上传照片时，将使用默认占位图。支持图片格式，大小不能超过 5MB。</p>
          </div>

          <div class="avatar-crop-manage-actions">
            <button type="button" class="ghost-button avatar-crop-action-btn" @click="emit('change-file')">修改照片</button>
            <button
              type="button"
              class="ghost-button avatar-crop-action-btn"
              :disabled="!canRemove"
              @click="emit('remove-file')"
            >
              移除照片
            </button>
          </div>

          <div class="avatar-crop-actions">
            <button type="button" class="ghost-button avatar-crop-action-btn" @click="handleCancel">取消</button>
            <button type="button" class="primary-button avatar-crop-action-btn" @click="confirmCrop">确认使用</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  file: { type: [File, Blob, Object], default: null },
  canRemove: { type: Boolean, default: false },
})

const emit = defineEmits(['cancel', 'confirm', 'change-file', 'remove-file'])

const cropFrameWidth = 240
const cropFrameHeight = 336
const cropOutputWidth = 500
const cropOutputHeight = 700

const imageUrl = ref('')
const imageNaturalWidth = ref(0)
const imageNaturalHeight = ref(0)
const baseScale = ref(1)
const userScale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragOriginX = ref(0)
const dragOriginY = ref(0)

const imageLayerStyle = computed(() => ({
  width: `${imageNaturalWidth.value * baseScale.value}px`,
  height: `${imageNaturalHeight.value * baseScale.value}px`,
  transform: `translate(${offsetX.value}px, ${offsetY.value}px) scale(${userScale.value})`,
}))

watch(
  () => props.file,
  async (file) => {
    resetState()
    if (!file) {
      clearObjectUrl()
      return
    }

    clearObjectUrl()
    imageUrl.value = URL.createObjectURL(file)
    await loadImageMeta(imageUrl.value)
    initTransform()
  },
)

onBeforeUnmount(clearObjectUrl)

function resetState() {
  imageNaturalWidth.value = 0
  imageNaturalHeight.value = 0
  baseScale.value = 1
  userScale.value = 1
  offsetX.value = 0
  offsetY.value = 0
  dragging.value = false
}

function clearObjectUrl() {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }
  imageUrl.value = ''
}

function loadImageMeta(url) {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => {
      imageNaturalWidth.value = image.naturalWidth || 0
      imageNaturalHeight.value = image.naturalHeight || 0
      resolve()
    }
    image.onerror = () => reject(new Error('image-load-failed'))
    image.src = url
  })
}

function initTransform() {
  if (!imageNaturalWidth.value || !imageNaturalHeight.value) {
    return
  }
  baseScale.value = Math.max(
    cropFrameWidth / imageNaturalWidth.value,
    cropFrameHeight / imageNaturalHeight.value,
  )
  userScale.value = 1
  clampOffset(0, 0)
}

function getImageDisplaySize(scaleValue = userScale.value) {
  return {
    width: imageNaturalWidth.value * baseScale.value * scaleValue,
    height: imageNaturalHeight.value * baseScale.value * scaleValue,
  }
}

function clampOffset(nextX, nextY, scaleValue = userScale.value) {
  const displaySize = getImageDisplaySize(scaleValue)
  const minX = Math.min(0, cropFrameWidth - displaySize.width)
  const minY = Math.min(0, cropFrameHeight - displaySize.height)
  offsetX.value = Math.min(0, Math.max(minX, nextX))
  offsetY.value = Math.min(0, Math.max(minY, nextY))
}

function handleWheel(event) {
  if (!imageUrl.value) {
    return
  }

  const nextScale = Math.min(4, Math.max(1, Number((userScale.value + (event.deltaY > 0 ? -0.08 : 0.08)).toFixed(2))))
  if (nextScale === userScale.value) {
    return
  }

  const rect = event.currentTarget.getBoundingClientRect()
  const pointX = event.clientX - rect.left
  const pointY = event.clientY - rect.top
  const scaleRatio = nextScale / userScale.value
  const nextX = pointX - (pointX - offsetX.value) * scaleRatio
  const nextY = pointY - (pointY - offsetY.value) * scaleRatio
  userScale.value = nextScale
  clampOffset(nextX, nextY, nextScale)
}

function startDrag(event) {
  if (!imageUrl.value) {
    return
  }
  dragging.value = true
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
  dragOriginX.value = offsetX.value
  dragOriginY.value = offsetY.value
  event.currentTarget.setPointerCapture?.(event.pointerId)
}

function handleDrag(event) {
  if (!dragging.value) {
    return
  }
  clampOffset(
    dragOriginX.value + event.clientX - dragStartX.value,
    dragOriginY.value + event.clientY - dragStartY.value,
  )
}

function stopDrag() {
  dragging.value = false
}

async function confirmCrop() {
  if (!props.file || !imageUrl.value || !imageNaturalWidth.value || !imageNaturalHeight.value) {
    emit('cancel')
    return
  }

  const canvas = document.createElement('canvas')
  canvas.width = cropOutputWidth
  canvas.height = cropOutputHeight
  const context = canvas.getContext('2d')
  if (!context) {
    emit('cancel')
    return
  }

  const image = new Image()
  image.src = imageUrl.value
  await new Promise((resolve, reject) => {
    image.onload = resolve
    image.onerror = () => reject(new Error('image-load-failed'))
  })

  const displayWidth = imageNaturalWidth.value * baseScale.value * userScale.value
  const displayHeight = imageNaturalHeight.value * baseScale.value * userScale.value
  const drawX = offsetX.value * (cropOutputWidth / cropFrameWidth)
  const drawY = offsetY.value * (cropOutputHeight / cropFrameHeight)
  const drawWidth = displayWidth * (cropOutputWidth / cropFrameWidth)
  const drawHeight = displayHeight * (cropOutputHeight / cropFrameHeight)

  context.fillStyle = '#ffffff'
  context.fillRect(0, 0, cropOutputWidth, cropOutputHeight)
  context.drawImage(image, drawX, drawY, drawWidth, drawHeight)

  canvas.toBlob((blob) => {
    if (!blob) {
      emit('cancel')
      return
    }
    const croppedFile = new File([blob], 'avatar.jpg', { type: 'image/jpeg' })
    emit('confirm', croppedFile)
  }, 'image/jpeg', 0.92)
}

function handleCancel() {
  emit('cancel')
}
</script>
