import { createTheme } from '@mui/system';

/**
 * JSON data for hex theme colors. Currently wrapped into a MUI theme, but not implemented via ThemeProviders (yet).
 *
 * @author Eric Doppelt
 */
const theme = createTheme({
    palette: {
        primary: {
            main: '#3f51b5',
            light: '#757de8',
            dark: '#002984',
        },
        secondary: {
            main: '#f57c00',
            light: '#ffad42',
            dark: '#bb4d00',
        }
    },
});

export default theme;