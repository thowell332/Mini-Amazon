import {React} from 'react';
import Typography from '@mui/material/Typography';
import '../../stylings/IconHeader.css'
/**
 * Icon formatted to be large and centered beneath the SearchBar.
 *
 * @author Eric Doppelt
 */
function IconHeader(props) {

  return (
    <div>
      <span className='centerImage'>
        {props.icon}
      </span>
      <div className='centerText'>
        <Typography variant='h3' color={'primary'}>
            {props.title}
        </Typography>
      </div>
    </div>
  )
}

export default IconHeader;