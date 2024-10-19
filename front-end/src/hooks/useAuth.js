import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../utils/axiosInstance";
import { useDispatch } from "react-redux";
import { loginReducer, logoutReducer } from "../redux/slices/auth";

function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const login = async (data) => {
    try {
      setIsLoading(true);
      //   const response = await axiosInstance.post("/users/login/", data);
      await dispatch(loginReducer(data));
      navigate("/app");
    } catch (error) {
      console.log(error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      //   const response = await axiosInstance.post("/users/login/", data);
      //   console.log(response);
      await dispatch(logoutReducer());
      navigate("/auth/login");
    } catch (error) {
      console.log(error);
    } finally {
      setIsLoading(false);
    }
  };

  const createAccount = async (data) => {
    try {
      setIsLoading(true);
      //   const response = await axiosInstance.post("/users/login/", data);
      //   console.log(response);
      await dispatch(loginReducer(data));
      navigate("/app");
    } catch (error) {
      console.log(error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login,
    logout,
    createAccount,
    isLoading,
  };
}

export default useAuth;
