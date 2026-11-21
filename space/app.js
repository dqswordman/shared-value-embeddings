const groups=JSON.parse(document.querySelector('#evidence').textContent);
const groupSelect=document.querySelector('#group'),itemSelect=document.querySelector('#item'),body=document.querySelector('#results');
function element(tag,text){const node=document.createElement(tag);node.textContent=text;return node;}
function draw(){
  const current=groups[groupSelect.selectedIndex].items[itemSelect.selectedIndex];
  const list=document.createElement('dl');
  for(const entry of current.rows){const pair=document.createElement('div');pair.append(element('dt',entry.label),element('dd',entry.value));list.append(pair);}
  body.replaceChildren(element('h2',current.name),element('p',current.description),list);
  if(current.bars.length){const bars=document.createElement('div');bars.className='bars';for(const item of current.bars){
    const group=document.createElement('div'),label=element('div',item.label),track=document.createElement('div'),bar=document.createElement('i');
    label.className='bar-label';label.append(element('strong',item.value.toFixed(2)+'%'));track.className='track';bar.style.width=item.value+'%';track.append(bar);group.append(label,track);bars.append(group);}body.append(bars);}
  body.removeAttribute('data-changed');requestAnimationFrame(()=>body.setAttribute('data-changed',''));
}
function changeGroup(){itemSelect.replaceChildren(...groups[groupSelect.selectedIndex].items.map((x,i)=>new Option(x.name,String(i))));draw();}
groupSelect.addEventListener('change',changeGroup);itemSelect.addEventListener('change',draw);
