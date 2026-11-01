import { Platform } from 'react-native';

// One place to rename the app once the team picks a name.
export const APP_NAME = 'PataShala';
export const TEAM = 'Team Alchemy · Code Kernel ’26';

// Phones cannot use "localhost": they need the laptop's Wi-Fi address, e.g. http://192.168.1.10:8000
// (set EXPO_PUBLIC_API_URL in mobile/.env, or type it on the first screen).
export const DEFAULT_API =
  process.env.EXPO_PUBLIC_API_URL ?? (Platform.OS === 'web' ? 'http://localhost:8000' : 'http://192.168.1.10:8000');


// Official page that lists the SCERT textbooks (link not checked from this environment; test it on your phone).
export const SCERT_URL = 'https://scert.telangana.gov.in/e-Textbooks.htm';
