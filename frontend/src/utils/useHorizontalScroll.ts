import { nextTick, reactive, ref, watchEffect } from 'vue';

export function useHorizontalScroll(options: {
  scrollStep?: number
} = {}) {
  const {
    scrollStep = 200,
  } = options

  const container = ref<HTMLElement>();
  const attr = reactive({
    position: 0,
    canScroll: false,
  });

  watchEffect((onCleanup) => {
    if (!container.value) return;

    const handleScroll = () => {
      attr.position = container.value!.scrollLeft;
    }

    updateCanScroll();

    container.value.addEventListener('scroll', handleScroll);

    onCleanup(() => {
      container.value?.removeEventListener('scroll', handleScroll);
    });
  });

  const updateCanScroll = () => {
    nextTick(() => {
    if (!container.value) return;
      attr.canScroll = container.value.scrollWidth > container.value.clientWidth;
    })
  };

  const refresh = () => {
    updateCanScroll();
  };

  const scroll = (direction: 'left' | 'right' = 'right') => {
    if (!container.value) return;

    const scrollDistance = direction === 'right' ? scrollStep : -scrollStep;

    container.value.scrollBy({
      left: scrollDistance,
      behavior: 'smooth'
    });
  }

  return {
    container,
    scroll,
    refresh,
    attr,
  }
}
