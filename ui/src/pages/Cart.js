import IconHeader from '../components/IconHeader';
import SearchBar from '../components/SearchBar';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import theme from '../util/Theme';
import '../util/stylings/FullDiv.css'
/**
 * Cart page. 
 *
 * @author Eric Doppelt
 */
function Cart() {
    return (
      <div className="fullDiv">
        <SearchBar/>
        <IconHeader
          /* TODO: refactor this into a LargeIcon */
          icon={<ShoppingCartIcon sx={{width: 200, height: 200, color: theme.palette.secondary.light}}/>}
          title='Your Shopping Cart'
        />
      </div>
    );
}

export default Cart;