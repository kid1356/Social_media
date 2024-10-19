import { Navigate, Outlet } from "react-router-dom";
import { Stack } from "@mui/material";
import { useSelector } from "react-redux";
import SideBar from "./SideBar";

const DashboardLayout = () => {
  const { isLogin } = useSelector((state) => state?.auth);

  if (!isLogin) {
    return <Navigate to="/auth/login" />;
  }

  return (
    <Stack direction="row">
      {/* SideBar */}
      <SideBar />
      <Outlet />
    </Stack>
  );
};

export default DashboardLayout;
