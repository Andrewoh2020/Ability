import { defineStore } from 'pinia'

type AppListType = 'mix' | 'public' | 'private';

export const useModalStore = defineStore('modal', {
  state: () => ({
    showLogin: false,
    showEditProfile: false,
    showCreateSection: false,
    appList: {
      show: false,
      action: false,
      type: 'mix' as AppListType,
    },
    showAppList: false,
    appListType: 'mix' as AppListType,
  }),
  actions: {
    openAppList(type: AppListType) {
      this.appList.show = true;
      this.appList.type = type;
      this.appList.action = type !== 'mix';
    },
  },
})
