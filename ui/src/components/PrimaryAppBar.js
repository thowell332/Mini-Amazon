import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import {Link} from 'react-router-dom';
import Logo from '../components/Logo'

function PrimaryAppBar() {
  return (
    <div className="app-bar">
      <AppBar>
          <Toolbar>
            <IconButton>
              <MenuIcon/>
            </IconButton>
            {/* FIXME: Style this with CSS or altenrative. */}
            <div style={{marginLeft:20, marginTop:10}}>
              <Link to={'/'}>
                <Logo/>
              </Link>
            </div>
          </Toolbar>
        </AppBar>
    </div>
  );
}

export default PrimaryAppBar;

