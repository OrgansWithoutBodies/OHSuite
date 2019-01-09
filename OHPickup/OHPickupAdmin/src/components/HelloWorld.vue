<template>
  <div class="hello">
    <div class="filled"></div>
    <div class="empty"></div>
    <div v-for="donor in donors">
      <donor-card v-bind:donor="donor"/>
    </div>
    <h2>Essential Links</h2>
    <h1>{{ title }}</h1>
    <DonationCard/>
  </div>
</template>

<script>
import DonorCard from './DonorCard'
import DonationCard from './DonationCard'
export default {
  name: 'HelloWorld',
  components: {
    DonationCard,
    DonorCard
  },
  data () {
    return {
      donors: [{firstname: 'Test',
        lastname: 'Testone',
        address: '215 test ct',
        phone: '12345',
        email: 'test'},
      {firstname: 'Test',
        lastname: 'testos',
        address: '215 test ct',
        phone: '12345',
        email: 'test'}],
      msg: 'Welcome to Your Vue.js App',
      title: 'V'
    }
  }
}
const fill = document.querySelector('.filled')
const empties = document.querySelectorAll('.empty')
for (const empty of empties) {
  empty.addEventListener('dragover', dragOver)
  empty.addEventListener('dragenter', dragEnter)
  empty.addEventListener('dragleave', dragLeave)
  empty.addEventListener('drop', dragDrop)
}
function dragStart () {
  this.className += ' hold'
  setTimeout(() => this.className = 'invisible', 0)
}
function dragEnd () {
  this.className = 'filled'
}
function dragOver (e) {
  e.preventDefault()
}
function dragLeave () {
  this.className = 'empty'
}
function dragDrop () {
  this.className = 'empty'
  this.append(fill)
}
function dragEnter (e) {
  e.preventDefault()
  this.className += ' hover'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
<!--Drag Drop-->
.empty{
  background:#ff0000;
  display:inline-block;
  height:150px;
  width:150px;
  margin:10px;
  border:3px;
  border-style:solid;
  top:5px;
  left:5px;
  border-color: #ffffff;
}
.filled{
  background:#0000ff;
  position:relative;
  height:130px;
  width:130px;
  margin:10px;
  color:#ffffff;
}
.hover{
  border-style:dashed;
}
.invisible{
  display:none;
}
</style>
