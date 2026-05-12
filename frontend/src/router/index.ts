import { createRouter, createWebHistory } from 'vue-router';

import { useUserStore } from '@/stores/user';
import { attemptAutoLogin } from '@/utils/attemptAutoLogin';

import DefaultLayout from '@/layouts/Default.vue';
import DashbordLayout from '@/layouts/Dashbord.vue';

import HomePage from '@/pages/Home.vue';
import StudioPage from '@/pages/Studio.vue';
import LoginPage from '@/pages/Login.vue';
import AppDetailPage from '@/pages/AppDetail.vue';
import AppCommunityPage from '@/pages/AppCommunity.vue';
import AuthCallbackPage from '@/pages/AuthCallback.vue';
import UserCommunityPage from '@/pages/UserCommunity.vue';
import UserConnectionsPage from '@/pages/UserConnections.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: LoginPage,
    },
    {
      path: '/',
      component: DashbordLayout,
      children: [
        { path: '', component: HomePage },
      ],
    },
    {
      path: '/',
      component: DashbordLayout,
      children: [
        { path: 'myapps', component: StudioPage },
      ],
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: 'me', component: UserCommunityPage },
        { path: 'users/:id/community', component: UserCommunityPage },
        { path: 'users/:id/connections', component: UserConnectionsPage },
      ],
    },
    {
      path: '/apps/:id/community',
      component: AppCommunityPage,
    },
    {
      path: '/a/:id',
      component: AppCommunityPage,
    },
    {
      path: '/projects/:id',
      component: AppDetailPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/p/:id',
      component: AppDetailPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/auth/callback',
      component: AuthCallbackPage,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
});

router.beforeEach(async (to, _from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  const userStore = useUserStore();
  if (requiresAuth && !userStore.isAuthenticated) {
    try {
      await attemptAutoLogin();
    } catch (_) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
      return;
    }
  }

  next();
});

export default router;
