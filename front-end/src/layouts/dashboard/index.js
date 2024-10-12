import { Navigate, Outlet } from "react-router-dom";
import { Stack } from '@mui/material';
import SideBar from "./SideBar";
import { useEffect } from "react";

const isAuthenticated = false;

const DashboardLayout = () => {
  
  const auth = JSON.parse(localStorage.getItem('auth'));
  if (!auth.isLogin) {
    <Navigate to='/auth/login' />;
  }

  return (
    <Stack direction='row'>
      {/* SideBar */}
      <SideBar />
      <Outlet />
    </Stack>

  );
};

export default DashboardLayout;
