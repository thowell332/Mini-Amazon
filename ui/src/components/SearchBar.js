import {React, useState} from 'react';
import theme from '../util/Theme';

import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Drawer from '@mui/material/Drawer';
import Divider from '@mui/material/Drawer';

import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';

import {Link} from 'react-router-dom';
import Logo from './Logo'

/**
 * Search bar component.
 * 
 * @author Eric Doppelt
 */
function SearchBar() {

  const [openDrawer, setOpenDrawer] = useState(false);

  const links = ['/', '/cart']
  const pageNames = ['Home', 'Cart']
  const icons = [<HomeIcon/>, <ShoppingCartIcon/>]

  return (
    
    <div className="app-bar">
      {/* AppBar with Search, Login Button, etc. incoming.*/}
      <AppBar
        sx={{
          backgroundColor: theme.palette.primary.main
        }}
        >
          <Toolbar>
            <IconButton
              onClick={() => setOpenDrawer(true)}
            >
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
      
        {/* Drawer with more comprehensive functionaliy.*/}

        <Drawer
          anchor={'left'}
          open={openDrawer}
          onClose={() => setOpenDrawer(false)}
          >
          <div style={{backgroundColor: theme.palette.primary.main, paddingLeft: 50, paddingTop: 20}}>
            <Logo/>
          </div>
          <Divider/>
          <List
            sx = {{
              backgroundColor: theme.palette.primary.main,
              height: '100vh',
              width: 200,
              textDecoration: 'none',
            }}
            >
            {/*----HOME----*/}
            {links.map((link, index) => (
              <Link to={link} style={{ color: theme.palette.secondary.light, textDecoration: 'none'}}>
              <ListItem key={pageNames[index]} sx={{paddingLeft: 2.5}}>
                <ListItemIcon style={{color: theme.palette.secondary.light}}>
                  {icons[index]}
                </ListItemIcon>
                <ListItemText primary={pageNames[index]} primaryTypographyProps={{variant: 'body1'}}/>
              </ListItem>
            </Link>
            ))}
          </List>
        </Drawer>
      </div>
    );
  }

export default SearchBar;