import { Component } from '@angular/core';

@Component({
  selector: 'my-app',
  template: `
    <h1>{{title}}</h1>
    <nav>
      <a routerLink="/transitions" routerLinkActive="active">Transitions</a>
      <a routerLink="/strategies" routerLinkActive="active">Strategies</a>
    </nav>
    <router-outlet></router-outlet>
  `,
  styleUrls: ['./app.component.css'],
})

export class AppComponent {
  title = 'Tour of Quant';
}

