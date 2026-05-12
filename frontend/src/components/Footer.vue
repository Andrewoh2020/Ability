<script setup lang="ts">
import Logo from '@/components/Logo.vue';
</script>

<template>
  <footer
    class="flex justify-between items-center text-white py-[20px] bg-[black] page-align"
  >
    <div class="flex md:flex-col justify-between items-center md:items-start w-full h-full">
      <Logo />
      <div class="w-[135px] md:w-fit text-[12px] text-end">All rights reserved. Copyright © 2025, Ability</div>
    </div>
    <div class="hidden md:flex gap-[16px]">
      <div class="flex flex-col gap-[16px] w-[120px] text-[14px]">
        <div class="text-[16px]">Discover</div>
        <RouterLink to="">Pricing</RouterLink>
        <RouterLink to="">Enterprise</RouterLink>
        <RouterLink to="">Learn</RouterLink>
      </div>
      <div class="flex flex-col gap-[16px] w-[120px] text-[14px]">
        <div class="text-[16px]">Legal</div>
        <RouterLink to="">Privacy policy</RouterLink>
        <RouterLink to="">Terms & conditions</RouterLink>
      </div>
      <div class="flex flex-col gap-[16px] w-[120px]">
        <div class="text-[16px]">Socials</div>
        <div class="flex gap-[16px]">
          <a href="" target="_blank">
            <img src="@/assets/facebook-icon.svg" alt="facebook" class="size-[24px]">
          </a>
          <a href="" target="_blank">
            <img src="@/assets/linkedin-icon.svg" alt="linkedin" class="size-[24px]">
          </a>
          <a href="" target="_blank">
            <img src="@/assets/instagram-icon.svg" alt="instagram" class="size-[24px]">
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>

</style>
