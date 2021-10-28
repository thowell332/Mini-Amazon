import React from 'react';
import LogoImage from '../../images/logo.png'

/**
 * Logo image wrapped into a component.
 *
 * @author Eric Doppelt
 */
function Logo() {

  return (
    <div className='logo'>
        <img alt='logo' height='30' width='auto' src={LogoImage}/>
    </div>
  );
}

export default Logo;
