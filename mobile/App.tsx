import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Navigator } from './src/nav';
import { AuthProvider } from './src/store';
import Connect from './src/screens/Connect';
import Welcome from './src/screens/Welcome';
import Login from './src/screens/Login';
import StudentReg from './src/screens/StudentReg';
import TeacherReg from './src/screens/TeacherReg';
import StudentHome from './src/screens/StudentHome';
import SubjectHub from './src/screens/SubjectHub';
import Practice from './src/screens/Practice';
import Progress from './src/screens/Progress';
import Settings from './src/screens/Settings';
import ForgotPin from './src/screens/ForgotPin';
import Report from './src/screens/Report';
import Result from './src/screens/Result';
import Explainer from './src/screens/Explainer';
import Replay from './src/screens/Replay';
import TeacherHome from './src/screens/TeacherHome';
import Roster from './src/screens/Roster';
import StudentDetail from './src/screens/StudentDetail';

const screens: Record<string, React.ComponentType<any>> = {
  Connect, Welcome, Login, ForgotPin, Settings, StudentReg, TeacherReg, StudentHome, SubjectHub, Progress, Practice, Report, Result, Explainer, Replay, TeacherHome, Roster, StudentDetail,
};

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <StatusBar style="light" />
        <Navigator screens={screens} initial={{ name: 'Connect' }} />
      </AuthProvider>
    </SafeAreaProvider>
  );
}
