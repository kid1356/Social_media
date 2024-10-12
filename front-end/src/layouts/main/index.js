import { Container, Stack } from "@mui/material";
import React, { useEffect } from "react";
import { Navigate, Outlet } from "react-router-dom";
import Logo from '../../assets/Images/logo.ico'

const isAuthenticated = false;

const MainLayout = () => {
  const auth = JSON.parse(localStorage.getItem('auth'));

  if (auth?.isLogin) {
    <Navigate to='/app' />;
  }

  return (
    <>
      <Container sx={{ mt: 5 }} maxWidth='sm'>
        <Stack spacing={5}>
          <Stack sx={{ width: '100%' }} direction='column' alignItems={'center'}>
            <img style={{ height: 120, width: 120 }} src={Logo} alt="Logo" />
          </Stack>
        </Stack>
        <Outlet />
      </Container>

    </>
  );
};

export default MainLayout;
