import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TransitionsComponent }   from './transitions.component';
import { StrategiesComponent }      from './strategies.component';
import { TransitionDetailComponent }  from './transition-detail.component';
import { StrategyDetailComponent }  from './strategy-detail.component';



const routes: Routes = [
  { path: '', redirectTo: '/transitions', pathMatch: 'full' },
  { path: 'transitions',  component: TransitionsComponent },
  { path: 'transition/detail/:id', component: TransitionDetailComponent },
  { path: 'strategy/detail/:name', component: StrategyDetailComponent },
  { path: 'strategies',     component: StrategiesComponent }
];


@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})


export class AppRoutingModule {}

