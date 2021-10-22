import {React} from 'react';
import theme from '../util/Theme';
import Typography from '@mui/material/Typography';


const centerImage = {
  display: 'block',
  marginLeft: 'auto',
  marginRight: 'auto',
  marginTop: '100px',
  width: '200px',
}

const centerText = {
    display: 'block',
    marginLeft: 'auto',
    marginRight: 'auto',
    width: '420px',
  }

/**
 * Icon formatted to be large and centered beneath the SearchBar.
 *
 * @author Eric Doppelt
 */
function IconHeader(props) {

  return (
    <div className="icon-header">
      <span
        style={centerImage}
        >
          {props.icon}
      </span>
      <span
        style={centerText}
        >
            <Typography variant='h3' sx={{color: theme.palette.primary.main}}>
                {props.title}
            </Typography>
      </span>
    
    </div>
  )
}

export default IconHeader;