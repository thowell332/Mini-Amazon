import {React, useState} from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Typography from '@mui/material/Typography';
import '../../stylings/Cart.css';
import { Button } from '@mui/material';

/**
 * Icon formatted to be large and centered beneath the SearchBar.
 *
 * @author Eric Doppelt
 */

/**
 * Need to show:
 *   - Product Name
 *   - Seller Name
 *   - Quantity
 *   - Unit Price
 *   - Total Item Price
 *   - Total Price at Bottom
 */

 var mock_data = [
    {
      id: 1,
      product_name: 'Guitar',
      seller_name: 'Thomas Bowel',
      quantity: 2,
      price: '20.99'
    },
  
    {
      id: 2,
      product_name: 'Drums',
      seller_name: 'Jordan Castleguy',
      quantity: 5,
      price: '6.90'
    },
  ]

  const columns = [
    { field: 'product_name', headerName: 'Product', width: 250 },
    { field: 'seller_name', headerName: 'Seller', width: 250 },
    { field: 'quantity', headerName: 'Quantity', type: 'number', width: 150, editable: true},
    { field: 'price', headerName: 'Unit Price', width: 160},
    {
      field: 'item_price',
      headerName: 'Total Price',
      width: 160,
      type: 'number',
      valueGetter: (params) => (Number(params.getValue(params.id, 'quantity') * params.getValue(params.id, 'price')).toFixed(2))
    },
  ];
  
function CartTable() {

    const [totalPrice, setTotalPrice] = useState(0);

  return (
      <div>
        <div className='table'>
            <DataGrid
                rows={mock_data}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                checkboxSelection
            />
        </div>

        <div className='totalPrice'>
          <Typography variant='h3' color={'primary'}>
              {'Total Price: $' + totalPrice}
          </Typography>
        </div>

        <div className='purchaseButton'>
          <Button fullWidth variant="contained" sx={{height: 50, fontSize: 18, borderRadius: 6}}>
            Purchase Cart
          </Button>    
        </div>
    </div>
  )
}

export default CartTable;