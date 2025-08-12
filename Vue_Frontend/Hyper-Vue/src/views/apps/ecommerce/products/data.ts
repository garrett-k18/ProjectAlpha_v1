import product1 from '@/assets/images/products/product-1.jpg'
import product2 from '@/assets/images/products/product-2.jpg'
import product3 from '@/assets/images/products/product-3.jpg'
import product4 from '@/assets/images/products/product-4.jpg'
import product5 from '@/assets/images/products/product-5.jpg'
import product6 from '@/assets/images/products/product-6.jpg'


const productData = [
  {
    image: product6,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Adirondack Chair',
    category: 'Aeron Chairs',
    date: '07/07/2018',
    price: '$65.94',
    quantity: 652,
    status: 'Active'
  },
  {
    image: product1,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Amazing Modern Chair',
    category: 'Aeron Chairs',
    date: '09/12/2018',
    price: '$148.66',
    quantity: 254,
    status: 'Active'
  },
  {
    image: product2,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Bean Bag Chair',
    category: 'Wooden Chairs',
    date: '06/30/2018',
    price: '$99',
    quantity: 1021,
    status: 'Deactive'
  },
  {
    image: product4,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Biblio Plastic Armchair',
    category: 'Wooden Chairs',
    date: '09/08/2018',
    price: '$8.99',
    quantity: 1874,
    status: 'Active'
  },
  {
    image: product3,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Bootecos Plastic Armchair',
    category: 'Wing Chairs',
    date: '07/15/2018',
    price: '$148.66',
    quantity: 485,
    status: 'Deactive'
  },
  {
    image: product3,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Branded Wooden Chair',
    category: 'Dining Chairs',
    date: '09/05/2018',
    price: '$68.32',
    quantity: 2541,
    status: 'Active'
  },
  {
    image: product5,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Cardan Armchair',
    category: 'Plastic Armchair',
    date: '08/02/2018',
    price: '$59.69',
    quantity: 26,
    status: 'Active'
  },
  {
    image: product4,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Designer Awesome Chair',
    category: 'Baby Chairs',
    date: '08/23/2018',
    price: '$112.00',
    quantity: 3540,
    status: 'Active'
  },
  {
    image: product4,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Eames Lounge Chair',
    category: 'Baby Chairs',
    date: '05/06/2018',
    price: '$39.5',
    quantity: 1254,
    status: 'Active'
  },
  {
    image: product5,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Farthingale Chair',
    category: 'Plastic Armchair',
    date: '04/09/2018',
    price: '$78.66',
    quantity: 524,
    status: 'Deactive'
  },
  {
    image: product3,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'The butterfly chair',
    category: 'Dining Chairs',
    date: '06/19/2018',
    price: '$58',
    quantity: 874,
    status: 'Active'
  },
  {
    image: product6,
    rating:Math.floor(Math.random()* (5 - 1 + 1) + 1),
    name: 'Unpowered aircraft',
    category: 'Wing Chairs',
    date: '03/24/2018',
    price: '$49',
    quantity: 204,
    status: 'Deactive'
  },
];

export { productData };