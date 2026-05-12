<script setup lang="ts">
import Compressor from 'compressorjs';
import { ref, computed, reactive } from 'vue';
import { ChevronDownIcon } from '@heroicons/vue/24/outline';

import { toast } from '@/utils/toast';
import { useUserStore } from '@/stores/user';
import locationData from '@/config/location';
import { updateUserInfo } from '@/services/user';

import DefaultAvatar from '@/components/DefaultAvatar.vue';
import LoadingButton from '@/components/LoadingButton.vue';


const emit = defineEmits<{
  'updated': [];
}>();

const loading = ref(false);
const userStore = useUserStore();
const fullName = ref(userStore.profile?.full_name || '');
const avatarUrl = ref(userStore.profile?.avatar_url || '');
const uploadedImage = reactive({
  name: '',
  src: '',
  file: null as File | null,
});
const fileInputRef = ref<HTMLInputElement>();

const bio = ref(userStore.profile?.bio || '');
const bioRef = ref<HTMLTextAreaElement>();
let defaultDay = '';
let defaultMonth = '';
let defaultYear = '';
if (userStore.profile?.birthday) {
  const [year, month, day] = userStore.profile.birthday.split('-');
  defaultYear = year!;
  defaultMonth = month!;
  defaultDay = day!;
}
const selectedDay = ref(defaultDay);
const selectedMonth = ref(defaultMonth);
const selectedYear = ref(defaultYear);
const selectedCountry = ref(userStore.profile?.country || '');
const selectedCity = ref(userStore.profile?.city || '');
const days = ref(Array.from({ length: 31 }, (_, i) =>
  (i + 1).toString().padStart(2, '0')
));
const months = ref(Array.from({ length: 12 }, (_, i) =>
  (i + 1).toString().padStart(2, '0')
));
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 100 }, (_, i) =>
    (currentYear - i).toString()
  )
});
const interestValues = ref<string[]>(userStore.profile?.interests || []);
const interests = [
  { value: 'finance', label: 'Finance' },
  { value: 'parenting', label: 'Parenting' },
  { value: 'productivity', label: 'Productivity' },
  { value: 'wellness', label: 'Wellness' },
]
const countries = locationData.countries;
const citiesByCountry = locationData.cities;

const updateTextareaHeight = async () => {
  if (bioRef.value) {
    bioRef.value.style.height = '52px';
    bioRef.value.style.overflowY = 'hidden';
    const newHeight = Math.max(bioRef.value.scrollHeight, 52);
    bioRef.value.style.height = newHeight + 'px';
    bioRef.value.style.overflowY = 'auto';
  }
}

const triggerUpload = () => {
  fileInputRef.value?.click();
};

const handleChangeFile = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    toast.warning('Please select an image file');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    toast.warning('Image size should be less than 5MB');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e: ProgressEvent<FileReader>) => {
    uploadedImage.file = file;
    uploadedImage.src = (e.target as FileReader).result as string;
  };
  reader.readAsDataURL(file);
};

const submit = async () => {
  if (loading.value) return;
  if (!fullName.value) {
    toast.error('Please enter full_name');
    return;
  }

  loading.value = true;

  try {
    const formData = new FormData();

    formData.append('full_name', fullName.value);
    formData.append('bio', bio.value);
    if (selectedYear.value && selectedMonth.value && selectedDay.value) {
      formData.append('birthday', `${selectedYear.value}-${selectedMonth.value}-${selectedDay.value}`);
    }
    formData.append('country', selectedCountry.value);
    formData.append('city', selectedCity.value);
    interestValues.value.forEach(interest => {
      formData.append('interests[]', interest);
    });

    if (uploadedImage.file) {
      const compressedFile = await new Promise((resolve, reject) => {
        new Compressor(uploadedImage.file!, {
          quality: 0.8,
          maxWidth: 512,
          maxHeight: 512,
          mimeType: 'image/webp',
          success: resolve,
          error: reject,
        });
      }) as Blob;
      formData.append('file', compressedFile, 'avatar.webp');
    }

    const updatedProfile = await updateUserInfo(formData);
    userStore.updateProfile(updatedProfile);
    emit('updated');
  } catch (err) {
    console.error(err);
    toast.error('failed to update');
  } finally {
    loading.value = false;
  }
}

const interestSelectedLabels = computed(() => {
  if (interestValues.value.length === 0) return '';

  const labels = interestValues.value.map(value => {
    const item = interests.find(item => item.value === value);
    return item?.label || '';
  }).filter(Boolean)

  return labels.join(',');
})

const interestOptionSeleted = (value) => {
  return interestValues.value.includes(value);
}

const toggleInterestOption = (value) => {
  if (interestOptionSeleted(value)) {
    interestValues.value = interestValues.value.filter(v => v !== value);
  } else {
    interestValues.value = [...interestValues.value, value];
  }
}

const filteredCities = computed(() => {
  return selectedCountry.value ? citiesByCountry[selectedCountry.value] || [] : []
})

const onCountryChange = () => {
  selectedCity.value = '';
}
</script>

<template>
  <div class="flex flex-col gap-[24px]">
    <div class="text-[20px] font-bold">
      Edit profile
    </div>
    <div class="flex items-center gap-[12px]">
      <img
        v-if="uploadedImage.src || avatarUrl"
        :src="uploadedImage.src || avatarUrl"
        class="size-[80px] rounded-full"
      >
      <DefaultAvatar
        v-else
        class="size-[80px] bg-[#F2F2F2]"
      />
      <div class="text-[#999999] text-[14px] truncate">
        {{ uploadedImage.src ? uploadedImage.file?.name : 'Upload your profile' }}
      </div>
      <div
        class="flex items-center gap-[8px] !w-[fit-content] text-[white] py-[8px] px-[12px] ml-auto rounded-[40px] btn btn-neutral"
        @click="triggerUpload"
      >
        <img
          src="@/assets/upload-icon.svg"
          class="size-[16px]"
        >
        <div>Upload</div>
      </div>
      <input
        ref="fileInputRef"
        type="file"
        name="file"
        accept="image/*"
        class="!hidden"
        @change="handleChangeFile"
      >
    </div>
    <div class="flex flex-col gap-[24px]">
      <div class="flex flex-col gap-[12px]">
        <div class="flex justify-between items-center">
          <div class="text-[18px]">
            Full name
          </div>
          <div class="text-[#666666] text-[14px]">
            {{ fullName.length }}/20
          </div>
        </div>
        <input
          v-model="fullName"
          type="text"
          class="w-full p-[16px] rounded-[40px] bg-[#F2F2F2]"
          placeholder="Enter full name"
          maxlength="20"
        >
      </div>
      <div class="h-[1px] bg-[#999999]" />
      <div class="flex gap-[8px]">
        <img
          src="@/assets/bulb-icon.svg"
          class="size-[24px]"
        >
        <div>
          Get the best recommendations: The more details you share below (like your bio, location, and interests), the better we can match you with great mini-app ideas and content you'll love.
          <span class="font-bold">Your profile information is always kept private and secure.</span>
        </div>
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="flex justify-between items-center">
          <div class="text-[18px]">
            Bio
          </div>
          <div class="text-[#666666] text-[14px]">
            {{ bio.length }}/150
          </div>
        </div>
        <textarea
          ref="bioRef"
          v-model="bio"
          type="text"
          class="w-full h-[52px] p-[16px] rounded-[40px] bg-[#F2F2F2] resize-none"
          placeholder="Tell the community about yourself"
          maxlength="150"
          @input="updateTextareaHeight"
        />
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          Date of birth
        </div>
        <div class="flex justify-between gap-[12px]">
          <select
            v-model="selectedDay"
            class="w-full !h-[52px] !px-[16px] cursor-pointer rounded-[40px] border-0 bg-[#F2F2F2] select"
          >
            <option
              value=""
              disabled
            >
              DD
            </option>
            <option
              v-for="day in days"
              :key="day"
              :value="day"
            >
              {{ day }}
            </option>
          </select>
          <select
            v-model="selectedMonth"
            class="w-full !h-[52px] !px-[16px] cursor-pointer rounded-[40px] border-0 bg-[#F2F2F2] select"
          >
            <option
              value=""
              disabled
            >
              MM
            </option>
            <option
              v-for="month in months"
              :key="month"
              :value="month"
            >
              {{ month }}
            </option>
          </select>
          <select
            v-model="selectedYear"
            class="w-full !h-[52px] !px-[16px] cursor-pointer rounded-[40px] border-0 bg-[#F2F2F2] select"
          >
            <option
              value=""
              disabled
            >
              YYYY
            </option>
            <option
              v-for="year in years"
              :key="`${year}`"
              :value="`${year}`"
            >
              {{ year }}
            </option>
          </select>
        </div>
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          Country
        </div>
        <select
          v-model="selectedCountry"
          class="w-full !h-[52px] !px-[16px] cursor-pointer rounded-[40px] border-0 bg-[#F2F2F2] select"
          @change="onCountryChange"
        >
          <option
            value=""
            disabled
          >
            Select your country
          </option>
          <option
            v-for="country in countries"
            :key="country"
            :value="country"
          >
            {{ country }}
          </option>
        </select>
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          City
        </div>
        <select
          v-model="selectedCity"
          :disabled="!selectedCountry"
          class="w-full !h-[52px] !px-[16px] cursor-pointer rounded-[40px] border-0 bg-[#F2F2F2] select"
        >
          <option
            value=""
            disabled
          >
            Select your city
          </option>
          <option
            v-for="city in filteredCities"
            :key="city"
            :value="city"
          >
            {{ city }}
          </option>
        </select>
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          Interest
        </div>
        <div class="relative dropdown">
          <div
            tabindex="0"
            role="button"
            class="text-[#999999] p-[16px] cursor-pointer rounded-[28px] bg-[#F2F2F2] "
          >
            <div class="flex justify-between items-center text-[18px] mb-[8px]">
              <div class="truncate">
                {{ interestSelectedLabels || 'Select your interest categories' }}
              </div>
              <ChevronDownIcon class="size-[16px] text-black flex-shrink-0" />
            </div>
            <div>The more interests you select, the better we can match you with useful and relevant mini-apps you'll love.</div>
          </div>
          <ul
            tabindex="0"
            class="absolute top-[-10px] translate-y-[-100%] flex-nowrap w-full max-h-[400px] p-[4px] overflow-y-auto bg-white shadow-md rounded-box menu dropdown-content"
          >
            <li
              v-for="item in interests"
              :key="item.value"
              class="leading-none"
            >
              <label class="label cursor-pointer">
                <input
                  type="checkbox"
                  :checked="interestOptionSeleted(item.value)"
                  class="checkbox checkbox-neutral"
                  @change="toggleInterestOption(item.value)"
                >
                <span class="label-text">{{ item.label }}</span>
              </label>
            </li>
          </ul>
        </div>
      </div>
      <LoadingButton
        :loading="loading"
        class="md:w-[fit-content] px-[14px] py-[16px] md:ml-auto rounded-[40px] btn-neutral"
        @click="submit"
      >
        Save changes
      </LoadingButton>
    </div>
  </div>
</template>
