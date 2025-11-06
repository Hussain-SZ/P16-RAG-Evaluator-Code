// import { useState } from 'react'
import './App.css'
import Welcome from './pages/Welcome.tsx'
import Signup from './pages/Signup.tsx'
import Login from './pages/Login.tsx'
import Home from './pages/Home.tsx'
import AccountSettings from './pages/AccountSettings.tsx'
import MyReports from './pages/MyReports.tsx'
import { RequestResetPassword, ResetPassword } from './pages/ResetPassword.tsx'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';

function App() {

  return (
    <Router>
      <Routes>
        <Route path = "/" element={<Welcome/>}/>
        <Route path = "/register" element={<Signup/>}/>
        <Route path = "/login" element={<Login/>}/>
        <Route path = "/home" element={<Home/>}/>
        <Route path = "/my-reports" element={<MyReports/>}/>
        <Route path = "/account-settings" element={<AccountSettings/>}/>
        <Route path = "/request-reset-password" element={<RequestResetPassword/>}/>
        <Route path = "/reset-password" element={<ResetPassword/>}/>


      </Routes>
    </Router>
  );
}

export default App
