import IconHeader from '../components/general/IconHeader';
import SearchBar from '../components/general/SearchBar';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import '../stylings/FullDiv.css'
import '../stylings/Cart.css'
import CartReceipt from '../components/cart/CartReceipt';

/**
 * Cart page. 
 *
 * @author Eric Doppelt
 */

function Cart() {

    return (
      <div className="fullDiv">
        <SearchBar/>
        <div className='iconHeader'>
          <IconHeader
            icon={<ShoppingCartIcon color='secondary' style={{fontSize: 150}}/>}
            title='Your Shopping Cart'
          />
        </div>
        <div className='receipt'>
          <CartReceipt/>
        </div>
        </div>
    );
}

export default Cart;